import { TestBed } from '@angular/core/testing';
import {
  ActivatedRouteSnapshot,
  Router,
  RouterStateSnapshot,
  UrlTree,
} from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';

import { AuthGuard } from './auth.guard';
import { AuthService } from '../services/auth.service';

describe('AuthGuard', () => {
  let guard: AuthGuard;
  let mockAuthService: Partial<AuthService>;
  let router: Router;

  beforeEach(() => {
    // Create AuthService spy with the methods we'll use
    mockAuthService = {
      isLoggedIn: jest.fn(),
      hasRole: jest.fn()
    };

    TestBed.configureTestingModule({
      imports: [RouterTestingModule],
      providers: [
        AuthGuard,
        { provide: AuthService, useValue: mockAuthService },
      ],
    });

    guard = TestBed.inject(AuthGuard);
    router = TestBed.inject(Router);
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });

  it('should allow access when user is logged in and no role is required', () => {
    // Arrange
    jest.spyOn(mockAuthService, 'isLoggedIn').mockReturnValue(true);
    const route = new ActivatedRouteSnapshot();
    route.data = {};

    const state = { url: '/home' } as RouterStateSnapshot;

    // Act
    const result = guard.canActivate(route, state);

    // Assert
    expect(result).toBe(true);
    expect(mockAuthService.isLoggedIn).toHaveBeenCalled();
  });

  it('should allow access when user is logged in and has the required role', () => {
    // Arrange
    jest.spyOn(mockAuthService, 'isLoggedIn').mockReturnValue(true);
    jest.spyOn(mockAuthService, 'hasRole').mockReturnValue(true);

    const route = new ActivatedRouteSnapshot();
    route.data = { role: 'parent' };

    const state = { url: '/children' } as RouterStateSnapshot;

    // Act
    const result = guard.canActivate(route, state);

    // Assert
    expect(result).toBe(true);
    expect(mockAuthService.isLoggedIn).toHaveBeenCalled();
    expect(mockAuthService.hasRole).toHaveBeenCalledWith('parent');
  });

  it('should redirect to home when user is logged in but does not have the required role', () => {
    // Arrange
    jest.spyOn(mockAuthService, 'isLoggedIn').mockReturnValue(true);
    jest.spyOn(mockAuthService, 'hasRole').mockReturnValue(false);

    const urlTree = {} as UrlTree;
    const createUrlTreeSpy = jest.spyOn(router, 'createUrlTree').mockReturnValue(urlTree);

    const route = new ActivatedRouteSnapshot();
    route.data = { role: 'parent' };

    const state = { url: '/children' } as RouterStateSnapshot;

    // Act
    const result = guard.canActivate(route, state);

    // Assert
    expect(mockAuthService.isLoggedIn).toHaveBeenCalled();
    expect(mockAuthService.hasRole).toHaveBeenCalledWith('parent');
    expect(createUrlTreeSpy).toHaveBeenCalledWith(['/home']);
    expect(result).toBe(urlTree);
  });

  it('should redirect to login when user is not logged in', () => {
    // Arrange
    jest.spyOn(mockAuthService, 'isLoggedIn').mockReturnValue(false);

    const urlTree = {} as UrlTree;
    const createUrlTreeSpy = jest.spyOn(router, 'createUrlTree').mockReturnValue(urlTree);

    const route = new ActivatedRouteSnapshot();
    const state = { url: '/home' } as RouterStateSnapshot;

    // Act
    const result = guard.canActivate(route, state);

    // Assert
    expect(mockAuthService.isLoggedIn).toHaveBeenCalled();
    expect(createUrlTreeSpy).toHaveBeenCalledWith(['/login'], {
      queryParams: { returnUrl: '/home' },
    });
    expect(result).toBe(urlTree);
  });
});