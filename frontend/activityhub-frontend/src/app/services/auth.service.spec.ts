import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { Router } from '@angular/router';

import { AuthService, User, AuthResponse } from './auth.service';
import { environment } from '../../environments/environment';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;
  let router: Router;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        HttpClientTestingModule,
        RouterTestingModule
      ],
      providers: [AuthService]
    });

    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
    router = TestBed.inject(Router);

    // Clear localStorage before each test
    localStorage.clear();
  });

  afterEach(() => {
    // Verify that there are no outstanding requests
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('register', () => {
    it('should send a POST request to register endpoint', () => {
      // Arrange
      const mockUser: AuthResponse = {
        message: 'User registered successfully',
        user: {
          user_id: '123',
          email: 'test@example.com',
          name: 'Test User',
          role: 'parent',
          created_at: 1645123456
        }
      };
      
      // Act
      service.register('test@example.com', 'Test User', 'password').subscribe(response => {
        // Assert
        expect(response).toEqual(mockUser);
      });

      // Assert request
      const req = httpMock.expectOne(`${environment.apiUrl}/register`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual({
        email: 'test@example.com',
        name: 'Test User',
        password: 'password',
        role: 'parent'
      });

      // Respond with mock data
      req.flush(mockUser);
    });

    it('should include parent_id when role is child', () => {
      // Arrange
      const mockUser: AuthResponse = {
        message: 'User registered successfully',
        user: {
          user_id: '456',
          email: 'child@example.com',
          name: 'Child User',
          role: 'child',
          created_at: 1645123456
        }
      };
      
      // Act
      service.register('child@example.com', 'Child User', 'password', 'child', 'parent123')
        .subscribe(response => {
          // Assert
          expect(response).toEqual(mockUser);
        });

      // Assert request
      const req = httpMock.expectOne(`${environment.apiUrl}/register`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual({
        email: 'child@example.com',
        name: 'Child User',
        password: 'password',
        role: 'child',
        parent_id: 'parent123'
      });

      // Respond with mock data
      req.flush(mockUser);
    });
  });

  describe('login', () => {
    it('should send a POST request to login endpoint and store user data', () => {
      // Arrange
      const mockLoginResponse: AuthResponse = {
        message: 'Login successful',
        user: {
          user_id: '123',
          email: 'test@example.com',
          name: 'Test User',
          role: 'parent',
          created_at: 1645123456
        },
        token: 'mock-jwt-token'
      };
      
      // Act
      service.login('test@example.com', 'password').subscribe(response => {
        // Assert
        expect(response).toEqual(mockLoginResponse);
        expect(service.currentUserValue).toEqual(mockLoginResponse.user);
        expect(localStorage.getItem('currentUser')).toBe(JSON.stringify(mockLoginResponse.user));
        expect(localStorage.getItem('token')).toBe('mock-jwt-token');
      });

      // Assert request
      const req = httpMock.expectOne(`${environment.apiUrl}/login`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual({
        email: 'test@example.com',
        password: 'password'
      });

      // Respond with mock data
      req.flush(mockLoginResponse);
    });
  });

  describe('logout', () => {
    it('should clear localStorage and navigate to login page', () => {
      // Arrange
      const navigateSpy = spyOn(router, 'navigate');
      const mockUser: User = {
        user_id: '123',
        email: 'test@example.com',
        name: 'Test User',
        role: 'parent',
        created_at: 1645123456
      };
      
      localStorage.setItem('currentUser', JSON.stringify(mockUser));
      localStorage.setItem('token', 'mock-jwt-token');
      localStorage.setItem('tokenExpiration', new Date(Date.now() + 3600000).toISOString());

      // Act
      service.logout();

      // Assert
      expect(localStorage.getItem('currentUser')).toBeNull();
      expect(localStorage.getItem('token')).toBeNull();
      expect(localStorage.getItem('tokenExpiration')).toBeNull();
      expect(service.currentUserValue).toBeNull();
      expect(navigateSpy).toHaveBeenCalledWith(['/login']);
    });
  });

  describe('isLoggedIn', () => {
    it('should return true if valid token exists', () => {
      // Arrange
      localStorage.setItem('token', 'mock-jwt-token');
      localStorage.setItem('tokenExpiration', new Date(Date.now() + 3600000).toISOString());

      // Act
      const result = service.isLoggedIn();

      // Assert
      expect(result).toBe(true);
    });

    it('should return false if token is missing', () => {
      // Act
      const result = service.isLoggedIn();

      // Assert
      expect(result).toBe(false);
    });

    it('should return false and logout if token is expired', () => {
      // Arrange
      const logoutSpy = spyOn(service, 'logout');
      localStorage.setItem('token', 'mock-jwt-token');
      localStorage.setItem('tokenExpiration', new Date(Date.now() - 3600000).toISOString());

      // Act
      const result = service.isLoggedIn();

      // Assert
      expect(result).toBe(false);
      expect(logoutSpy).toHaveBeenCalled();
    });
  });

  describe('hasRole', () => {
    it('should return true if user has the specified role', () => {
      // Arrange
      const mockUser: User = {
        user_id: '123',
        email: 'test@example.com',
        name: 'Test User',
        role: 'parent',
        created_at: 1645123456
      };
      
      spyOnProperty(service, 'currentUserValue').and.returnValue(mockUser);

      // Act
      const result = service.hasRole('parent');

      // Assert
      expect(result).toBe(true);
    });

    it('should return false if user does not have the specified role', () => {
      // Arrange
      const mockUser: User = {
        user_id: '123',
        email: 'test@example.com',
        name: 'Test User',
        role: 'parent',
        created_at: 1645123456
      };
      
      spyOnProperty(service, 'currentUserValue').and.returnValue(mockUser);

      // Act
      const result = service.hasRole('child');

      // Assert
      expect(result).toBe(false);
    });

    it('should return false if no user is logged in', () => {
      // Arrange
      spyOnProperty(service, 'currentUserValue').and.returnValue(null);

      // Act
      const result = service.hasRole('parent');

      // Assert
      expect(result).toBe(false);
    });
  });
});
