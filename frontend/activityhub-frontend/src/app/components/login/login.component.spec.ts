import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { RouterTestingModule } from '@angular/router/testing';
import { Router } from '@angular/router';
import { ActivatedRoute } from '@angular/router';
import { of, throwError } from 'rxjs';

import { LoginComponent } from './login.component';
import { AuthService } from '../../services/auth.service';

describe('LoginComponent', () => {
  let component: LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;
  let authServiceSpy: jasmine.SpyObj<AuthService>;
  let router: Router;

  beforeEach(async () => {
    // Create AuthService spy with the methods we'll use
    const spy = jasmine.createSpyObj('AuthService', ['login', 'isLoggedIn']);

    await TestBed.configureTestingModule({
      declarations: [LoginComponent],
      imports: [ReactiveFormsModule, RouterTestingModule],
      providers: [
        { provide: AuthService, useValue: spy },
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              queryParams: {},
            },
          },
        },
      ],
    }).compileComponents();

    authServiceSpy = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    router = TestBed.inject(Router);
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;

    // Initialize isLoggedIn to return false by default
    authServiceSpy.isLoggedIn.and.returnValue(false);

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize the form with empty email and password', () => {
    // Assert
    expect(component.loginForm.controls['email'].value).toBe('');
    expect(component.loginForm.controls['password'].value).toBe('');
  });

  it('should redirect to home if already logged in', () => {
    // Reset the component to create it again with our setup
    fixture.destroy();

    // Arrange - set up before creating component
    authServiceSpy.isLoggedIn.and.returnValue(true);
    const navigateSpy = spyOn(router, 'navigate');

    // Create component again and trigger lifecycle hooks
    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    // Assert
    expect(navigateSpy).toHaveBeenCalledWith(['/home']);
  });

  it('should return returnUrl from query params', () => {
    // Arrange
    const route = TestBed.inject(ActivatedRoute);
    (route.snapshot.queryParams as any) = { returnUrl: '/challenges' };

    // Act
    component.ngOnInit();

    // Assert
    expect(component.returnUrl).toBe('/challenges');
  });

  it('should mark form as invalid when email is empty', () => {
    // Arrange
    component.loginForm.controls['email'].setValue('');
    component.loginForm.controls['password'].setValue('password123');

    // Act
    component.onSubmit();

    // Assert
    expect(component.loginForm.valid).toBeFalsy();
    expect(component.submitted).toBeTruthy();
  });

  it('should mark form as invalid when password is empty', () => {
    // Arrange
    component.loginForm.controls['email'].setValue('test@example.com');
    component.loginForm.controls['password'].setValue('');

    // Act
    component.onSubmit();

    // Assert
    expect(component.loginForm.valid).toBeFalsy();
    expect(component.submitted).toBeTruthy();
  });

  it('should call auth service login when form is valid', () => {
    // Arrange
    authServiceSpy.login.and.returnValue(
      of({
        message: 'Login successful',
        user: {
          user_id: '123',
          email: 'test@example.com',
          name: 'Test User',
          role: 'parent',
          created_at: 1645123456,
        },
        token: 'mock-token',
      })
    );

    const navigateSpy = spyOn(router, 'navigate');

    component.loginForm.controls['email'].setValue('test@example.com');
    component.loginForm.controls['password'].setValue('password123');

    // Act
    component.onSubmit();

    // Assert
    expect(authServiceSpy.login).toHaveBeenCalledWith(
      'test@example.com',
      'password123'
    );
    expect(navigateSpy).toHaveBeenCalledWith(['/home']);
  });

  it('should handle login error', () => {
    // Arrange
    const errorMessage = 'Invalid email or password';
    authServiceSpy.login.and.returnValue(throwError(errorMessage));

    component.loginForm.controls['email'].setValue('test@example.com');
    component.loginForm.controls['password'].setValue('wrong-password');

    // Act
    component.onSubmit();

    // Assert
    expect(authServiceSpy.login).toHaveBeenCalledWith(
      'test@example.com',
      'wrong-password'
    );
    expect(component.error).toBe(errorMessage);
    expect(component.loading).toBeFalse();
  });

  it('should navigate to the return URL after successful login', () => {
    // Arrange
    authServiceSpy.login.and.returnValue(
      of({
        message: 'Login successful',
        user: {
          user_id: '123',
          email: 'test@example.com',
          name: 'Test User',
          role: 'parent',
          created_at: 1645123456,
        },
        token: 'mock-token',
      })
    );

    const navigateSpy = spyOn(router, 'navigate');
    component.returnUrl = '/challenges';

    component.loginForm.controls['email'].setValue('test@example.com');
    component.loginForm.controls['password'].setValue('password123');

    // Act
    component.onSubmit();

    // Assert
    expect(navigateSpy).toHaveBeenCalledWith(['/challenges']);
  });

  // DOM Testing
  it('should display error message when error is set', () => {
    // Arrange
    component.error = 'Invalid credentials';
    fixture.detectChanges();

    // Assert
    const errorElement = fixture.nativeElement.querySelector('.alert-danger');
    expect(errorElement.textContent).toContain('Invalid credentials');
  });

  it('should disable login button and show spinner when loading', () => {
    // Arrange
    component.loading = true;
    fixture.detectChanges();

    // Assert
    const buttonElement = fixture.nativeElement.querySelector('button');
    const spinnerElement =
      fixture.nativeElement.querySelector('.spinner-border');

    expect(buttonElement.disabled).toBeTrue();
    expect(spinnerElement).toBeTruthy();
  });
});
