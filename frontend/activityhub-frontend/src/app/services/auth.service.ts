// src/app/services/auth.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError, from } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { Router } from '@angular/router';
import { environment } from '../../environments/environment';
import {
  signUp,
  signIn,
  signOut,
  fetchAuthSession,
  getCurrentUser,
  fetchUserAttributes,
  JWT,
} from '@aws-amplify/auth';

export interface User {
  user_id: string;
  email: string;
  name: string;
  role: string;
  created_at?: number;
}

export interface AuthResponse {
  message: string;
  user: User;
  tokens?: {
    id_token: string;
    access_token: string;
    expires_in: number;
  };
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private apiUrl = environment.apiUrl;
  private currentUserSubject: BehaviorSubject<User | null>;
  public currentUser: Observable<User | null>;
  private tokenRefreshTimeout: any;

  constructor(private http: HttpClient, private router: Router) {
    // Try to get user from localStorage on service initialization
    const storedUser = localStorage.getItem('currentUser');
    this.currentUserSubject = new BehaviorSubject<User | null>(
      storedUser ? JSON.parse(storedUser) : null
    );
    this.currentUser = this.currentUserSubject.asObservable();

    // Check if there's a valid session on init
    this.checkCurrentAuthentication();

    // Set up token refresh interval
    this.setupTokenRefreshInterval();
  }

  private async checkCurrentAuthentication(): Promise<void> {
    try {
      // Try to get the current session
      const session = await fetchAuthSession();

      if (!session.tokens) {
        return;
      }

      // Get the current authenticated user
      const userResult = await getCurrentUser();
      const userAttributes = await fetchUserAttributes();

      // Create user object from attributes
      const user: User = {
        user_id: userResult.userId,
        email: userAttributes.email || '',
        name: userAttributes.name || '',
        role: userAttributes['custom:role'] || 'user',
      };

      // Store user in local storage
      localStorage.setItem('currentUser', JSON.stringify(user));

      // Store tokens
      localStorage.setItem(
        'id_token',
        (session.tokens.idToken as JWT).toString()
      );
      localStorage.setItem(
        'access_token',
        session.tokens.accessToken.toString()
      );

      // Set expiration time (typically 1 hour)
      const expiry = new Date();
      expiry.setHours(expiry.getHours() + 1);
      localStorage.setItem('token_expiration', expiry.toISOString());

      // Update current user
      this.currentUserSubject.next(user);
    } catch (error) {
      console.log('No active session found or error fetching session');
      // Clear any potentially stale data
      localStorage.removeItem('currentUser');
      localStorage.removeItem('id_token');
      localStorage.removeItem('access_token');
      localStorage.removeItem('token_expiration');
      this.currentUserSubject.next(null);
    }
  }

  public get currentUserValue(): User | null {
    return this.currentUserSubject.value;
  }

  register(
    email: string,
    name: string,
    password: string,
    role: string = 'parent',
    parent_id?: string
  ): Observable<AuthResponse> {
    // Prepare attributes
    const userAttributes: Record<string, string> = {
      email,
      name,
      'custom:role': role,
    };

    if (role === 'child' && parent_id) {
      userAttributes['custom:parentId'] = parent_id;
    }

    // Use signUp from v6
    return from(
      signUp({
        username: email,
        password,
        options: {
          userAttributes,
        },
      })
    ).pipe(
      map((response) => {
        // Return formatted response
        return {
          message: 'User registered successfully',
          user: {
            user_id: response.userId as string,
            email,
            name,
            role,
          },
        };
      }),
      catchError((error) => {
        console.error('Registration error:', error);
        return throwError(() => error.message || 'Registration failed');
      })
    );
  }

  login(email: string, password: string): Observable<AuthResponse> {
    // Create a proper Observable that handles all async operations
    return from(
      // This IIFE handles all the async operations
      (async () => {
        try {
          // 1. Sign in with username/password
          await signIn({ username: email, password });

          try {
            // 2. Get session with tokens
            const session = await fetchAuthSession();

            if (!session.tokens) {
              throw new Error('No tokens in session');
            }

            // 3. Get user details
            const userResult = await getCurrentUser();
            const userAttributes = await fetchUserAttributes();

            // 4. Create user object
            const user: User = {
              user_id: userResult.userId,
              email: userAttributes.email || email,
              name: userAttributes.name || '',
              role: userAttributes['custom:role'] || 'user',
            };

            // 5. Store in local storage
            localStorage.setItem('currentUser', JSON.stringify(user));
            localStorage.setItem(
              'id_token',
              (session.tokens.idToken as JWT).toString()
            );
            localStorage.setItem(
              'access_token',
              session.tokens.accessToken.toString()
            );

            // 6. Set token expiration (typically 1 hour)
            const expiry = new Date();
            expiry.setHours(expiry.getHours() + 1);
            localStorage.setItem('token_expiration', expiry.toISOString());

            // 7. Update current user
            this.currentUserSubject.next(user);

            // 8. Return success response
            return {
              message: 'Login successful',
              user,
              tokens: {
                id_token: (session.tokens.idToken as JWT).toString(),
                access_token: session.tokens.accessToken.toString(),
                expires_in: 3600, // 1 hour in seconds
              },
            } as AuthResponse;
          } catch (sessionError) {
            console.error('Session error:', sessionError);
            throw sessionError;
          }
        } catch (error: any) {
          console.error('Login error:', error);
          throw new Error(error.message || 'Login failed');
        }
      })()
    ).pipe(
      catchError((error) => throwError(() => error.message || 'Login failed'))
    );
  }

  async logout(): Promise<void> {
    try {
      // Sign out from Cognito
      await signOut();

      // Clear local storage
      localStorage.removeItem('currentUser');
      localStorage.removeItem('id_token');
      localStorage.removeItem('access_token');
      localStorage.removeItem('token_expiration');

      // Clear token refresh timer
      if (this.tokenRefreshTimeout) {
        clearTimeout(this.tokenRefreshTimeout);
        this.tokenRefreshTimeout = null;
      }

      // Update the current user subject
      this.currentUserSubject.next(null);

      // Navigate to login page
      this.router.navigate(['/login']);
    } catch (error) {
      console.error('Logout error:', error);
    }
  }

  // Check if user is logged in
  isLoggedIn(): boolean {
    const token = localStorage.getItem('access_token');
    const expiration = localStorage.getItem('token_expiration');

    if (!token || !expiration) {
      return false;
    }

    // Check if token is expired
    const expirationDate = new Date(expiration);
    if (expirationDate <= new Date()) {
      this.logout(); // Automatically logout if token is expired
      return false;
    }

    return true;
  }

  // Check user role
  hasRole(role: string): boolean {
    const currentUser = this.currentUserValue;
    return currentUser !== null && currentUser.role === role;
  }

  // Refresh token - in v6 this uses the forceRefresh flag
  // src/app/services/auth.service.ts - refreshTokens method
  refreshTokens(): Observable<any> {
    return from(fetchAuthSession({ forceRefresh: true })).pipe(
      map((session) => {
        if (!session.tokens) {
          throw new Error('No tokens in refreshed session');
        }

        // Update tokens in local storage
        localStorage.setItem(
          'id_token',
          (session.tokens.idToken as JWT).toString()
        );
        localStorage.setItem(
          'access_token',
          session.tokens.accessToken.toString()
        );

        // Update expiration time
        const expiry = new Date();
        expiry.setHours(expiry.getHours() + 1);
        localStorage.setItem('token_expiration', expiry.toISOString());

        // Return new tokens
        return {
          id_token: (session.tokens.idToken as JWT).toString(),
          access_token: session.tokens.accessToken.toString(),
          expires_in: 3600, // 1 hour in seconds
        };
      }),
      catchError((error) => {
        console.error('Token refresh error:', error);
        this.logout();
        return throwError(() => 'Session expired. Please log in again.');
      })
    );
  }

  // Set up a periodic token refresh
  private setupTokenRefreshInterval(): void {
    // Clear any existing interval
    if (this.tokenRefreshTimeout) {
      clearTimeout(this.tokenRefreshTimeout);
    }

    // We'll refresh the token every 45 minutes (assuming 1hr expiry)
    const refreshInterval = 45 * 60 * 1000; // 45 minutes in milliseconds

    this.tokenRefreshTimeout = setInterval(() => {
      // Only refresh if user is logged in
      if (this.isLoggedIn()) {
        this.refreshTokens().subscribe({
          next: () => console.log('Token refreshed successfully'),
          error: (err) => console.error('Failed to refresh token:', err),
        });
      }
    }, refreshInterval);
  }
}
