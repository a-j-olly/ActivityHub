import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { Router } from '@angular/router';
import { environment } from '../../environments/environment';

export interface User {
  user_id: string;
  email: string;
  name: string;
  role: string;
  created_at: number;
}

export interface AuthResponse {
  message: string;
  user: User;
  token?: string;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private apiUrl = environment.apiUrl;
  private currentUserSubject: BehaviorSubject<User | null>;
  public currentUser: Observable<User | null>;
  private tokenExpirationTimer: any;

  constructor(private http: HttpClient, private router: Router) {
    // Try to get user from localStorage on service initialization
    const storedUser = localStorage.getItem('currentUser');
    this.currentUserSubject = new BehaviorSubject<User | null>(
      storedUser ? JSON.parse(storedUser) : null
    );
    this.currentUser = this.currentUserSubject.asObservable();
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
    const registrationData: any = {
      email,
      name,
      password,
      role,
    };

    // Only include parent_id if it's provided and role is 'child'
    if (role === 'child' && parent_id) {
      registrationData.parent_id = parent_id;
    }

    return this.http
      .post<AuthResponse>(`${this.apiUrl}/register`, registrationData)
      .pipe(catchError(this.handleError));
  }

  login(email: string, password: string): Observable<AuthResponse> {
    return this.http
      .post<AuthResponse>(`${this.apiUrl}/login`, { email, password })
      .pipe(
        tap((response) => {
          if (response && response.token) {
            this.setSession(response);
          }
        }),
        catchError(this.handleError)
      );
  }

  logout(): void {
    // Clear authentication data
    localStorage.removeItem('currentUser');
    localStorage.removeItem('token');
    localStorage.removeItem('tokenExpiration');

    // Clear timeout if it exists
    if (this.tokenExpirationTimer) {
      clearTimeout(this.tokenExpirationTimer);
    }

    // Update the current user subject
    this.currentUserSubject.next(null);

    // Navigate to login page
    this.router.navigate(['/login']);
  }

  // Check if user is logged in
  isLoggedIn(): boolean {
    const token = localStorage.getItem('token');
    const expiration = localStorage.getItem('tokenExpiration');

    if (!token || !expiration) {
      return false;
    }

    // Check if token is expired
    const expirationDate = new Date(expiration);
    if (expirationDate <= new Date()) {
      this.logout();
      return false;
    }

    return true;
  }

  // Check user role
  hasRole(role: string): boolean {
    const currentUser = this.currentUserValue;
    return currentUser !== null && currentUser.role === role;
  }

  // Refresh token (if needed in the future)
  refreshToken(): Observable<any> {
    // This would be implemented when a token refresh endpoint is available
    // For now, just log the user out if their token is expired
    return throwError('Token refresh not implemented');
  }

  // Private helper methods
  private setSession(authResult: AuthResponse): void {
    // Store the user in local storage
    localStorage.setItem('currentUser', JSON.stringify(authResult.user));
    localStorage.setItem('token', authResult.token!);

    // Calculate token expiration (assuming 1 hour from now)
    const expirationDate = new Date(new Date().getTime() + 60 * 60 * 1000);
    localStorage.setItem('tokenExpiration', expirationDate.toISOString());

    // Update the current user subject
    this.currentUserSubject.next(authResult.user);

    // Set timer for auto logout
    this.autoLogout(60 * 60 * 1000); // 1 hour
  }

  private autoLogout(expirationDuration: number): void {
    this.tokenExpirationTimer = setTimeout(() => {
      this.logout();
    }, expirationDuration);
  }

  private handleError(error: any): Observable<never> {
    let errorMessage = 'An unknown error occurred!';

    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Error: ${error.error.message}`;
    } else if (error.error && error.error.message) {
      // Server-side error with a message
      errorMessage = error.error.message;
    } else if (error.status) {
      // Server-side error with a status code but no message
      switch (error.status) {
        case 400:
          errorMessage = 'Bad request';
          break;
        case 401:
          errorMessage = 'Unauthorized';
          break;
        case 404:
          errorMessage = 'Not found';
          break;
        default:
          errorMessage = `Error Code: ${error.status}`;
      }
    }

    console.error('Authentication error:', error);
    return throwError(errorMessage);
  }
}
