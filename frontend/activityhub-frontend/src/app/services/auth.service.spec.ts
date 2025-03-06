import { TestBed, fakeAsync, tick } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { Router } from '@angular/router';
import { of, throwError, BehaviorSubject } from 'rxjs';

import { AuthResponse, AuthService, User } from './auth.service';

// Mock for AWS Amplify Auth functions
import * as Auth from '@aws-amplify/auth';

describe('AuthService', () => {
  let service: AuthService;
  let router: Router;
  
  // Sample test user
  const testUser: User = {
    user_id: 'test-user-id',
    email: 'test@example.com',
    name: 'Test User',
    role: 'parent',
    created_at: 1645123456
  };
  
  // Setup and mocks before each test
  beforeEach(() => {
    // Create spies for all the Auth methods we use
    jest.spyOn(Auth, 'signUp').mockResolvedValue({
      userId: 'test-user-id',
      isSignUpComplete: true,
      nextStep: { signUpStep: 'CONFIRM_SIGN_UP', codeDeliveryDetails: {} }
    });

    jest.spyOn(Auth, 'signIn').mockResolvedValue({
      isSignedIn: true,
      nextStep: { signInStep: 'DONE' }
    });

    jest.spyOn(Auth, 'signOut').mockResolvedValue(undefined);

    jest.spyOn(Auth, 'getCurrentUser').mockResolvedValue({
      userId: 'test-user-id',
      username: 'test@example.com'
    });

    jest.spyOn(Auth, 'fetchUserAttributes').mockResolvedValue({
      email: 'test@example.com',
      name: 'Test User',
      'custom:role': 'parent'
    });

    jest.spyOn(Auth, 'fetchAuthSession').mockResolvedValue({
      tokens: {
        idToken: {
          payload: {},
          toString: () => 'test-id-token'
        },
        accessToken: {
          payload: {},
          toString: () => 'test-access-token'
        }
      }
    });

    // Clear localStorage before each test
    localStorage.clear();

    TestBed.configureTestingModule({
      imports: [
        HttpClientTestingModule, 
        RouterTestingModule.withRoutes([
          { path: 'login', component: {} as any }
        ])
      ],
      providers: [AuthService]
    });

    router = TestBed.inject(Router);
    // Spy on router navigate
    jest.spyOn(router, 'navigate');
  });

  // Clean up after each test
  afterEach(() => {
    jest.clearAllMocks();
    if (service) {
      // Clear any interval that might have been set up
      const refreshTimeout = (service as any).tokenRefreshTimeout;
      if (refreshTimeout) {
        clearInterval(refreshTimeout);
      }
    }
  });

  it('should be created', () => {
    service = TestBed.inject(AuthService);
    expect(service).toBeTruthy();
  });

  describe('hasRole', () => {
    it('should return true if user has the specified role', () => {
      // Create the service first
      service = TestBed.inject(AuthService);
      
      // Set private subject value
      (service as any).currentUserSubject = new BehaviorSubject<User | null>(testUser);
      
      // Test the hasRole method
      expect(service.hasRole('parent')).toBe(true);
      expect(service.hasRole('child')).toBe(false);
    });

    it('should return false if no user is logged in', () => {
      // Create the service first
      service = TestBed.inject(AuthService);
      
      // Set the private subject to have null value (no user logged in)
      (service as any).currentUserSubject = new BehaviorSubject<User | null>(null);
      
      // Test the hasRole method
      expect(service.hasRole('parent')).toBe(false);
    });
  });

  describe('checkCurrentAuthentication', () => {
    it('should clear storage if no session exists', async () => {
      // Setup some existing values to be cleared - use valid JSON!
      const testUser = {
        user_id: 'test-user-id',
        email: 'test@example.com',
        name: 'Test User',
        role: 'parent'
      };
      localStorage.setItem('currentUser', JSON.stringify(testUser));
      localStorage.setItem('id_token', 'old-token');
      localStorage.setItem('access_token', 'old-token');
      
      // Mock fetchAuthSession to reject for this test
      jest.spyOn(Auth, 'fetchAuthSession').mockRejectedValue(new Error('No current session'));
      
      // Create the service after setting up localStorage and mocks
      service = TestBed.inject(AuthService);
      
      // Call the method directly
      await (service as any).checkCurrentAuthentication();
      
      // Assert
      expect(localStorage.getItem('currentUser')).toBeNull();
      expect(localStorage.getItem('id_token')).toBeNull();
      expect(localStorage.getItem('access_token')).toBeNull();
    });
  });

  describe('register', () => {
    it('should call signUp with correct parameters', (done) => {
      // Create the service
      service = TestBed.inject(AuthService);
      
      // Act
      service
        .register('test@example.com', 'Test User', 'password123')
        .subscribe({
          next: (response) => {
            try {
              // Assert
              expect(response.message).toBe('User registered successfully');
              expect(response.user.user_id).toBe('test-user-id');
              expect(response.user.email).toBe('test@example.com');
              expect(response.user.name).toBe('Test User');
              expect(response.user.role).toBe('parent');

              // Verify signUp was called with correct params
              expect(Auth.signUp).toHaveBeenCalledWith({
                username: 'test@example.com',
                password: 'password123',
                options: {
                  userAttributes: {
                    email: 'test@example.com',
                    name: 'Test User',
                    'custom:role': 'parent'
                  }
                }
              });

              done();
            } catch (error) {
              done(error);
            }
          },
          error: (error) => done(error)
        });
    });

    it('should include parentId when role is child', (done) => {
      // Create the service
      service = TestBed.inject(AuthService);
      
      // Act
      service
        .register(
          'child@example.com',
          'Child User',
          'password123',
          'child',
          'parent-id'
        )
        .subscribe({
          next: (response) => {
            try {
              // Assert
              expect(response.user.role).toBe('child');

              // Verify signUp was called with parentId
              expect(Auth.signUp).toHaveBeenCalledWith(
                expect.objectContaining({
                  options: {
                    userAttributes: expect.objectContaining({
                      'custom:parentId': 'parent-id'
                    })
                  }
                })
              );

              done();
            } catch (error) {
              done(error);
            }
          },
          error: (error) => done(error)
        });
    });

    it('should handle registration error', (done) => {
      // Create the service
      service = TestBed.inject(AuthService);
      
      // Override mock to throw error
      jest.spyOn(Auth, 'signUp').mockRejectedValue(new Error('Email already exists'));

      // Act & Assert
      service
        .register('test@example.com', 'Test User', 'password123')
        .subscribe({
          next: () => done.fail('should have failed'),
          error: (error) => {
            try {
              expect(error).toBe('Email already exists');
              done();
            } catch (e) {
              done(e);
            }
          }
        });
    });
  });

  describe('login', () => {
    it('should authenticate and store user data', (done) => {
      // Create the service
      service = TestBed.inject(AuthService);
      
      // Act
      service.login('test@example.com', 'password123').subscribe({
        next: (result) => {
          try {
            // Assert
            expect(result).toBeTruthy();
            expect(result.user.user_id).toBe('test-user-id');
            expect(result.user.email).toBe('test@example.com');
            expect(result.user.name).toBe('Test User');
            expect(result.user.role).toBe('parent');

            // Verify tokens
            expect(result.tokens?.id_token).toBe('test-id-token');
            expect(result.tokens?.access_token).toBe('test-access-token');

            // Check local storage
            expect(localStorage.getItem('id_token')).toBe('test-id-token');
            expect(localStorage.getItem('access_token')).toBe('test-access-token');
            expect(localStorage.getItem('currentUser')).toBeTruthy();

            // Verify methods were called
            expect(Auth.signIn).toHaveBeenCalledWith({
              username: 'test@example.com',
              password: 'password123'
            });
            expect(Auth.fetchAuthSession).toHaveBeenCalled();
            expect(Auth.getCurrentUser).toHaveBeenCalled();
            expect(Auth.fetchUserAttributes).toHaveBeenCalled();

            done();
          } catch (error) {
            done(error);
          }
        },
        error: (error) => done(error)
      });
    });

    it('should handle login error properly', (done) => {
      // Create the service
      service = TestBed.inject(AuthService);
      
      // Mock error case with a consistent error return
      jest.clearAllMocks(); // Reset all mocks to ensure clean state
      jest.spyOn(Auth, 'signIn').mockRejectedValue(new Error('Invalid credentials'));
      
      // Act
      service.login('test@example.com', 'wrongpassword').subscribe({
        next: () => {
          done.fail('Should have failed');
        },
        error: (err) => {
          try {
            // Assert
            expect(err).toBe('Invalid credentials');
            expect(Auth.signIn).toHaveBeenCalledWith({
              username: 'test@example.com',
              password: 'wrongpassword'
            });
            done();
          } catch (error) {
            done(error);
          }
        }
      });
    }, 15000); // Increase timeout to handle potential delays
  });

  describe('refreshTokens', () => {
    it('should refresh tokens using fetchAuthSession with forceRefresh', (done) => {
      // Create the service
      service = TestBed.inject(AuthService);
      
      // Act
      service.refreshTokens().subscribe({
        next: (tokens) => {
          try {
            // Assert
            expect(tokens).toBeTruthy();
            expect(tokens.id_token).toBe('test-id-token');
            expect(tokens.access_token).toBe('test-access-token');

            // Verify localStorage was updated
            expect(localStorage.getItem('id_token')).toBe('test-id-token');
            expect(localStorage.getItem('access_token')).toBe('test-access-token');
            expect(localStorage.getItem('token_expiration')).toBeTruthy();

            // Verify forceRefresh was used
            expect(Auth.fetchAuthSession).toHaveBeenCalledWith({
              forceRefresh: true
            });

            done();
          } catch (error) {
            done(error);
          }
        },
        error: (error) => done(error)
      });
    });

    it('should handle token refresh errors and logout', (done) => {
      // Create the service
      service = TestBed.inject(AuthService);
      
      // Mock error case
      jest.spyOn(Auth, 'fetchAuthSession').mockRejectedValue(new Error('Session expired'));
      jest.spyOn(service, 'logout').mockResolvedValue();

      // Act
      service.refreshTokens().subscribe({
        next: () => done.fail('Should have failed'),
        error: (err) => {
          try {
            // Assert
            expect(err).toBe('Session expired. Please log in again.');
            expect(service.logout).toHaveBeenCalled();
            done();
          } catch (error) {
            done(error);
          }
        }
      });
    });
  });

  describe('logout', () => {
    it('should sign out, clear storage and navigate to login', async () => {
      // Create the service
      service = TestBed.inject(AuthService);
      
      // Arrange
      localStorage.setItem(
        'currentUser',
        JSON.stringify({
          user_id: 'test-user-id',
          email: 'test@example.com',
          name: 'Test User',
          role: 'parent',
        })
      );
      localStorage.setItem('id_token', 'test-id-token');
      localStorage.setItem('access_token', 'test-access-token');
      localStorage.setItem(
        'token_expiration',
        new Date(Date.now() + 3600000).toISOString()
      );

      // Act
      await service.logout();

      // Assert
      expect(Auth.signOut).toHaveBeenCalled();
      expect(localStorage.getItem('currentUser')).toBeNull();
      expect(localStorage.getItem('id_token')).toBeNull();
      expect(localStorage.getItem('access_token')).toBeNull();
      expect(localStorage.getItem('token_expiration')).toBeNull();
      expect(router.navigate).toHaveBeenCalledWith(['/login']);
    });
  });

  describe('isLoggedIn', () => {
    it('should return true if valid token exists', () => {
      // Create the service
      service = TestBed.inject(AuthService);
      
      // Arrange
      localStorage.setItem('access_token', 'test-access-token');
      localStorage.setItem(
        'token_expiration',
        new Date(Date.now() + 3600000).toISOString()
      );

      // Act & Assert
      expect(service.isLoggedIn()).toBe(true);
    });

    it('should return false if token is missing', () => {
      // Create the service
      service = TestBed.inject(AuthService);
      
      // Act & Assert
      expect(service.isLoggedIn()).toBe(false);
    });

    it('should return false and logout if token is expired', () => {
      // Create the service
      service = TestBed.inject(AuthService);
      
      // Arrange
      localStorage.setItem('access_token', 'test-access-token');
      localStorage.setItem(
        'token_expiration',
        new Date(Date.now() - 3600000).toISOString()
      );
      jest.spyOn(service, 'logout');

      // Act & Assert
      expect(service.isLoggedIn()).toBe(false);
      expect(service.logout).toHaveBeenCalled();
    });
  });
});