import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { HTTP_INTERCEPTORS, HttpClient, HttpErrorResponse } from '@angular/common/http';
import { RouterTestingModule } from '@angular/router/testing';
import { Router } from '@angular/router';

import { AuthInterceptor } from './auth.interceptor';

describe('AuthInterceptor', () => {
  let httpClient: HttpClient;
  let httpMock: HttpTestingController;
  let router: Router;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        HttpClientTestingModule,
        RouterTestingModule
      ],
      providers: [
        { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }
      ]
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
    localStorage.setItem('token', 'test-token');
    const testUrl = '/api/data';

    // Act
    httpClient.get(testUrl).subscribe();

    // Assert
    const httpRequest = httpMock.expectOne(testUrl);
    expect(httpRequest.request.headers.has('Authorization')).toBeTrue();
    expect(httpRequest.request.headers.get('Authorization')).toBe('Bearer test-token');
  });

  it('should not add an Authorization header when no token exists', () => {
    // Arrange
    const testUrl = '/api/data';

    // Act
    httpClient.get(testUrl).subscribe();

    // Assert
    const httpRequest = httpMock.expectOne(testUrl);
    expect(httpRequest.request.headers.has('Authorization')).toBeFalse();
  });

  it('should redirect to login page on 401 Unauthorized error', () => {
    // Arrange
    const navigateSpy = spyOn(router, 'navigate');
    const testUrl = '/api/data';

    // Act
    httpClient.get(testUrl).subscribe(
      () => fail('should have failed with 401 error'),
      (error: HttpErrorResponse) => {
        // Assert error is passed through
        expect(error.status).toBe(401);
      }
    );

    // Respond with 401
    const httpRequest = httpMock.expectOne(testUrl);
    httpRequest.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });

    // Assert navigation occurred
    expect(navigateSpy).toHaveBeenCalledWith(['/login']);
  });

  it('should not redirect on non-401 errors', () => {
    // Arrange
    const navigateSpy = spyOn(router, 'navigate');
    const testUrl = '/api/data';

    // Act
    httpClient.get(testUrl).subscribe(
      () => fail('should have failed with 404 error'),
      (error: HttpErrorResponse) => {
        // Assert error is passed through
        expect(error.status).toBe(404);
      }
    );

    // Respond with 404
    const httpRequest = httpMock.expectOne(testUrl);
    httpRequest.flush('Not Found', { status: 404, statusText: 'Not Found' });

    // Assert navigation did not occur
    expect(navigateSpy).not.toHaveBeenCalled();
  });
});
