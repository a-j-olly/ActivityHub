import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse,
} from '@angular/common/http';
import { Observable, throwError, BehaviorSubject, of } from 'rxjs';
import { catchError, filter, take, switchMap, finalize } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  private isRefreshing = false;
  // This subject tracks the access token refresh flow
  private tokenSubject: BehaviorSubject<string | null> = new BehaviorSubject<string | null>(null);

  constructor(private authService: AuthService) {}

  intercept(
    request: HttpRequest<unknown>,
    next: HttpHandler
  ): Observable<HttpEvent<unknown>> {
    // Get the auth token from localStorage
    const token = localStorage.getItem('access_token');

    // Clone the request and add the token if it exists
    if (token) {
      request = this.addToken(request, token);
    }

    // Pass on the cloned request
    return next.handle(request).pipe(
      catchError((error) => {
        if (error instanceof HttpErrorResponse && error.status === 401) {
          return this.handle401Error(request, next);
        }
        return throwError(() => error);
      })
    );
  }

  private addToken(request: HttpRequest<any>, token: string): HttpRequest<any> {
    return request.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  private handle401Error(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (!this.isRefreshing) {
      // Start refreshing
      this.isRefreshing = true;
      this.tokenSubject.next(null);

      // Attempt to refresh tokens
      return this.authService.refreshTokens().pipe(
        switchMap((tokens) => {
          // Refresh successful - update token subject with new token
          this.tokenSubject.next(tokens.access_token);
          
          // Retry the request with new token
          return next.handle(this.addToken(request, tokens.access_token));
        }),
        catchError((err) => {
          // Refresh failed - logout and propagate error
          this.authService.logout();
          return throwError(() => err);
        }),
        finalize(() => {
          // Always reset refreshing state when done
          this.isRefreshing = false;
        })
      );
    } else {
      // If refresh is already in progress, wait for the new token
      return this.tokenSubject.pipe(
        filter(token => token !== null),
        take(1),
        switchMap(token => {
          // Use the new token when it becomes available
          return next.handle(this.addToken(request, token!));
        })
      );
    }
  }
}