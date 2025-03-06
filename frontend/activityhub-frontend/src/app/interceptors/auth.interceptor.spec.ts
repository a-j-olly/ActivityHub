import { TestBed, fakeAsync, tick } from '@angular/core/testing';
import {
  HttpClientTestingModule,
  HttpTestingController,
} from '@angular/common/http/testing';
import {
  HTTP_INTERCEPTORS,
  HttpClient,
  HttpErrorResponse,
} from '@angular/common/http';
import { RouterTestingModule } from '@angular/router/testing';
import { Router } from '@angular/router';
import { of, throwError } from 'rxjs';

import { AuthInterceptor } from './auth.interceptor';
import { AuthService } from '../services/auth.service';

describe('AuthInterceptor', () => {
  let httpClient: HttpClient;
  let httpMock: HttpTestingController;
  let router: Router;
  let mockAuthService: Partial<AuthService>;

  beforeEach(() => {
    // Create AuthService mock with the methods we'll use
    mockAuthService = {
      refreshTokens: jest.fn(),
      logout: jest.fn(),
    };

    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule, RouterTestingModule],
      providers: [
        { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true },
        { provide: AuthService, useValue: mockAuthService },
      ],
    });

    httpClient = TestBed.inject(HttpClient);
    httpMock = TestBed.inject(HttpTestingController);
    router = TestBed.inject(Router);

    // Clear localStorage before each test
    localStorage.clear();
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should add an Authorization header with token', () => {
    // Arrange
    localStorage.setItem('access_token', 'test-token');
    const testUrl = '/api/data';

    // Act
    httpClient.get(testUrl).subscribe();

    // Assert
    const httpRequest = httpMock.expectOne(testUrl);
    expect(httpRequest.request.headers.has('Authorization')).toBe(true);
    expect(httpRequest.request.headers.get('Authorization')).toBe(
      'Bearer test-token'
    );

    // Complete the request
    httpRequest.flush({});
  });

  it('should not add an Authorization header when no token exists', () => {
    // Arrange
    const testUrl = '/api/data';

    // Act
    httpClient.get(testUrl).subscribe();

    // Assert
    const httpRequest = httpMock.expectOne(testUrl);
    expect(httpRequest.request.headers.has('Authorization')).toBe(false);

    // Complete the request
    httpRequest.flush({});
  });

  it('should attempt to refresh token on 401 Unauthorized error', fakeAsync(() => {
    // Arrange
    localStorage.setItem('access_token', 'expired-token');
    const testUrl = '/api/data';

    // Mock the token refresh response
    const refreshedTokens = {
      id_token: 'new-id-token',
      access_token: 'new-access-token',
      expires_in: 3600,
    };

    (mockAuthService.refreshTokens as jest.Mock).mockReturnValue(
      of(refreshedTokens)
    );

    // Act
    let responseData: any;
    let errorData: any;

    httpClient.get(testUrl).subscribe({
      next: (res) => (responseData = res),
      error: (err) => (errorData = err),
    });

    // Respond with 401 to first request
    const firstRequest = httpMock.expectOne(testUrl);
    expect(firstRequest.request.headers.get('Authorization')).toBe(
      'Bearer expired-token'
    );
    
    firstRequest.flush('Unauthorized', {
      status: 401,
      statusText: 'Unauthorized',
    });

    // Update localStorage as the real service would
    localStorage.setItem('access_token', 'new-access-token');

    // Need to advance the tick to process the refresh
    tick();

    // Verify the retried request has the new token
    const secondRequest = httpMock.expectOne(testUrl);
    expect(secondRequest.request.headers.get('Authorization')).toBe(
      'Bearer new-access-token'
    );

    // Complete the second request
    secondRequest.flush({ data: 'success' });

    // Ensure all async operations complete
    tick();

    // Assert
    expect(responseData).toEqual({ data: 'success' });
    expect(errorData).toBeUndefined();
    expect(mockAuthService.refreshTokens).toHaveBeenCalled();
  }));

  it('should logout if token refresh fails', fakeAsync(() => {
    // Arrange
    localStorage.setItem('access_token', 'expired-token');
    const testUrl = '/api/data';

    (mockAuthService.refreshTokens as jest.Mock).mockReturnValue(
      throwError(() => 'Failed to refresh token')
    );

    // Act
    let responseData: any;
    let errorData: any;

    httpClient.get(testUrl).subscribe({
      next: (res) => (responseData = res),
      error: (err) => (errorData = err),
    });

    // Respond with 401 to the request
    const httpRequest = httpMock.expectOne(testUrl);
    httpRequest.flush('Unauthorized', {
      status: 401,
      statusText: 'Unauthorized',
    });

    // Process all pending async tasks
    tick();

    // Assert
    expect(mockAuthService.refreshTokens).toHaveBeenCalled();
    expect(mockAuthService.logout).toHaveBeenCalled();
    expect(responseData).toBeUndefined();
    expect(errorData).toBe('Failed to refresh token');
  }));

  it('should not try to refresh token on non-401 errors', () => {
    // Arrange
    localStorage.setItem('access_token', 'valid-token');
    const testUrl = '/api/data';

    // Act
    let responseData: any;
    let errorData: any;

    httpClient.get(testUrl).subscribe({
      next: (res) => (responseData = res),
      error: (err) => (errorData = err),
    });

    // Respond with 404
    const httpRequest = httpMock.expectOne(testUrl);
    httpRequest.flush('Not Found', { status: 404, statusText: 'Not Found' });

    // Assert
    expect(mockAuthService.refreshTokens).not.toHaveBeenCalled();
    expect(mockAuthService.logout).not.toHaveBeenCalled();
    expect(errorData instanceof HttpErrorResponse).toBe(true);
    expect(errorData.status).toBe(404);
  });

  it('should handle queued requests during token refresh', fakeAsync(() => {
    // Arrange
    localStorage.setItem('access_token', 'expired-token');
    
    // Create a simple token refresh mock that returns tokens immediately
    (mockAuthService.refreshTokens as jest.Mock).mockImplementation(() => {
      // Update the token in localStorage (this is crucial)
      localStorage.setItem('access_token', 'new-access-token');
      // Return the tokens observable
      return of({
        id_token: 'new-id-token',
        access_token: 'new-access-token',
        expires_in: 3600
      });
    });
    
    // Act - Make first request that will trigger the 401
    let response1: any = null;
    httpClient.get('/api/data1').subscribe(res => response1 = res);
    
    // Get and handle first request
    const req1 = httpMock.expectOne('/api/data1');
    expect(req1.request.headers.get('Authorization')).toBe('Bearer expired-token');
    req1.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });
    
    // Process async tasks for the token refresh to complete
    tick(100);
    
    // Verify that first request is retried with new token
    const retried1 = httpMock.expectOne('/api/data1');
    expect(retried1.request.headers.get('Authorization')).toBe('Bearer new-access-token');
    
    // Complete the retried first request
    retried1.flush({ data: 'response1' });
    tick(10);
    
    // Make a second request after token has been refreshed
    let response2: any = null;
    httpClient.get('/api/data2').subscribe(res => response2 = res);
    
    // Verify second request uses the new token
    const req2 = httpMock.expectOne('/api/data2');
    expect(req2.request.headers.get('Authorization')).toBe('Bearer new-access-token');
    req2.flush({ data: 'response2' });
    
    // Process final tasks
    tick(10);
    
    // Verify responses
    expect(response1).toEqual({ data: 'response1' });
    expect(response2).toEqual({ data: 'response2' });
    
    // Verify no outstanding requests
    httpMock.verify();
  }));
});