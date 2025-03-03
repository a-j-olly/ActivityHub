import { Injectable } from '@angular/core';
import {
  CanActivate,
  ActivatedRouteSnapshot,
  RouterStateSnapshot,
  UrlTree,
  Router,
} from '@angular/router';
import { Observable } from 'rxjs';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root',
})
export class AuthGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ):
    | Observable<boolean | UrlTree>
    | Promise<boolean | UrlTree>
    | boolean
    | UrlTree {
    // Check if user is logged in
    if (this.authService.isLoggedIn()) {
      // Check if route has required role
      const requiredRole = route.data['role'] as string;
      if (requiredRole && !this.authService.hasRole(requiredRole)) {
        // If user doesn't have required role, redirect to home
        return this.router.createUrlTree(['/home']);
      }

      // User is authenticated and has required role (if any)
      return true;
    }

    // User is not logged in, redirect to login
    return this.router.createUrlTree(['/login'], {
      queryParams: { returnUrl: state.url },
    });
  }
}
