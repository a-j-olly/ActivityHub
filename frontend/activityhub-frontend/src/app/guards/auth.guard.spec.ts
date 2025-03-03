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
  let authService: jasmine.SpyObj<AuthService>;
  let router: Router;

  beforeEach(() => {
    // Create AuthService spy with the methods we'll use
    const authServiceSpy = jasmine.createSpyObj('AuthService', [
      'isLoggedIn',
      'hasRole',
    ]);

    TestBed.configureTestingModule({
      imports: [RouterTestingModule],
      providers: [
        AuthGuard,
        { provide: AuthService, useValue: authServiceSpy },
      ],
    });

    guard = TestBed.inject(AuthGuard);
    authService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    router = TestBed.inject(Router);
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });

  it('should allow access when user is logged in and no role is required', () => {
    // Arrange
    authService.isLoggedIn.and.returnValue(true);
    const route = new ActivatedRouteSnapshot();
    route.data = {};

    const state = { url: '/home' } as RouterStateSnapshot;

    // Act
    const result = guard.canActivate(route, state);

    // Assert
    expect(result).toBe(true);
    expect(authService.isLoggedIn).toHaveBeenCalled();
  });

  it('should allow access when user is logged in and has the required role', () => {
    // Arrange
    authService.isLoggedIn.and.returnValue(true);
    authService.hasRole.and.returnValue(true);

    const route = new ActivatedRouteSnapshot();
    route.data = { role: 'parent' };

    const state = { url: '/children' } as RouterStateSnapshot;

    // Act
    const result = guard.canActivate(route, state);

    // Assert
    expect(result).toBe(true);
    expect(authService.isLoggedIn).toHaveBeenCalled();
    expect(authService.hasRole).toHaveBeenCalledWith('parent');
  });

  it('should redirect to home when user is logged in but does not have the required role', () => {
    // Arrange
    authService.isLoggedIn.and.returnValue(true);
    authService.hasRole.and.returnValue(false);

    const navigateSpy = spyOn(router, 'createUrlTree');
    navigateSpy.and.returnValue({} as UrlTree);

    const route = new ActivatedRouteSnapshot();
    route.data = { role: 'parent' };

    const state = { url: '/children' } as RouterStateSnapshot;

    // Act
    guard.canActivate(route, state);

    // Assert
    expect(authService.isLoggedIn).toHaveBeenCalled();
    expect(authService.hasRole).toHaveBeenCalledWith('parent');
    expect(navigateSpy).toHaveBeenCalledWith(['/home']);
  });

  it('should redirect to login when user is not logged in', () => {
    // Arrange
    authService.isLoggedIn.and.returnValue(false);

    const navigateSpy = spyOn(router, 'createUrlTree');
    navigateSpy.and.returnValue({} as UrlTree);

    const route = new ActivatedRouteSnapshot();
    const state = { url: '/home' } as RouterStateSnapshot;

    // Act
    guard.canActivate(route, state);

    // Assert
    expect(authService.isLoggedIn).toHaveBeenCalled();
    expect(navigateSpy).toHaveBeenCalledWith(['/login'], {
      queryParams: { returnUrl: '/home' },
    });
  });
});
