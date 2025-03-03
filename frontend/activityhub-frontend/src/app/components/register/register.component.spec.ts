import {
  ComponentFixture,
  TestBed,
  fakeAsync,
  tick,
} from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { RouterTestingModule } from '@angular/router/testing';
import { Router } from '@angular/router';
import { of, throwError } from 'rxjs';

import { RegisterComponent } from './register.component';
import { AuthService } from '../../services/auth.service';

describe('RegisterComponent', () => {
  let component: RegisterComponent;
  let fixture: ComponentFixture<RegisterComponent>;
  let authServiceSpy: jasmine.SpyObj<AuthService>;
  let router: Router;

  beforeEach(async () => {
    // Create AuthService spy with the methods we'll use
    const spy = jasmine.createSpyObj('AuthService', ['register', 'isLoggedIn']);

    await TestBed.configureTestingModule({
      declarations: [RegisterComponent],
      imports: [ReactiveFormsModule, RouterTestingModule],
      providers: [{ provide: AuthService, useValue: spy }],
    }).compileComponents();

    authServiceSpy = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    router = TestBed.inject(Router);
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(RegisterComponent);
    component = fixture.componentInstance;

    // Initialize isLoggedIn to return false by default
    authServiceSpy.isLoggedIn.and.returnValue(false);

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize the form correctly', () => {
    // Assert
    expect(component.registerForm.controls['name'].value).toBe('');
    expect(component.registerForm.controls['email'].value).toBe('');
    expect(component.registerForm.controls['password'].value).toBe('');
    expect(component.registerForm.controls['confirmPassword'].value).toBe('');
    expect(component.registerForm.controls['role'].value).toBe('parent');
  });

  it('should redirect to home if already logged in', () => {
    // Reset the component to create it again with our setup
    fixture.destroy();

    // Arrange - set up before creating component
    authServiceSpy.isLoggedIn.and.returnValue(true);
    const navigateSpy = spyOn(router, 'navigate');

    // Create component again and trigger lifecycle hooks
    fixture = TestBed.createComponent(RegisterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    // Assert
    expect(navigateSpy).toHaveBeenCalledWith(['/home']);
  });

  it('should validate password match', () => {
    // Arrange
    component.registerForm.controls['password'].setValue('password123');
    component.registerForm.controls['confirmPassword'].setValue('different');

    // Act
    component.registerForm.updateValueAndValidity();

    // Assert
    expect(
      component.registerForm.controls['confirmPassword'].errors?.['mustMatch']
    ).toBeTruthy();
  });

  it('should validate password length', () => {
    // Arrange
    component.registerForm.controls['password'].setValue('short');

    // Act
    component.registerForm.updateValueAndValidity();

    // Assert
    expect(
      component.registerForm.controls['password'].errors?.['minlength']
    ).toBeTruthy();
  });

  it('should validate email format', () => {
    // Arrange
    component.registerForm.controls['email'].setValue('invalid-email');

    // Act
    component.registerForm.updateValueAndValidity();

    // Assert
    expect(
      component.registerForm.controls['email'].errors?.['email']
    ).toBeTruthy();
  });

  it('should not submit when form is invalid', () => {
    // Arrange
    component.registerForm.controls['name'].setValue('Test User');
    component.registerForm.controls['email'].setValue('test@example.com');
    component.registerForm.controls['password'].setValue('');
    component.registerForm.controls['confirmPassword'].setValue('');

    // Act
    component.onSubmit();

    // Assert
    expect(component.submitted).toBeTrue();
    expect(authServiceSpy.register).not.toHaveBeenCalled();
  });

  it('should call auth service register when form is valid', () => {
    // Arrange
    authServiceSpy.register.and.returnValue(
      of({
        message: 'Registration successful',
        user: {
          user_id: '123',
          email: 'test@example.com',
          name: 'Test User',
          role: 'parent',
          created_at: 1645123456,
        },
      })
    );

    component.registerForm.controls['name'].setValue('Test User');
    component.registerForm.controls['email'].setValue('test@example.com');
    component.registerForm.controls['password'].setValue('password123');
    component.registerForm.controls['confirmPassword'].setValue('password123');
    component.registerForm.controls['role'].setValue('parent');

    // Act
    component.onSubmit();

    // Assert
    expect(authServiceSpy.register).toHaveBeenCalledWith(
      'test@example.com',
      'Test User',
      'password123',
      'parent'
    );
    expect(component.success).toBe('Registration successful');
    expect(component.error).toBe('');
  });

  it('should navigate to login after successful registration', fakeAsync(() => {
    // Arrange
    authServiceSpy.register.and.returnValue(
      of({
        message: 'Registration successful',
        user: {
          user_id: '123',
          email: 'test@example.com',
          name: 'Test User',
          role: 'parent',
          created_at: 1645123456,
        },
      })
    );

    const navigateSpy = spyOn(router, 'navigate');

    component.registerForm.controls['name'].setValue('Test User');
    component.registerForm.controls['email'].setValue('test@example.com');
    component.registerForm.controls['password'].setValue('password123');
    component.registerForm.controls['confirmPassword'].setValue('password123');

    // Act
    component.onSubmit();

    // Wait for the setTimeout delay
    tick(1500);

    // Assert
    expect(navigateSpy).toHaveBeenCalledWith(['/login']);
  }));

  it('should handle registration error', () => {
    // Arrange
    const errorMessage = 'Email already exists';
    authServiceSpy.register.and.returnValue(throwError(errorMessage));

    component.registerForm.controls['name'].setValue('Test User');
    component.registerForm.controls['email'].setValue('test@example.com');
    component.registerForm.controls['password'].setValue('password123');
    component.registerForm.controls['confirmPassword'].setValue('password123');

    // Act
    component.onSubmit();

    // Assert
    expect(component.error).toBe(errorMessage);
    expect(component.success).toBe('');
    expect(component.loading).toBeFalse();
  });

  // DOM Testing
  it('should display success message when registration succeeds', () => {
    // Arrange
    authServiceSpy.register.and.returnValue(
      of({
        message: 'Registration successful',
        user: {
          user_id: '123',
          email: 'test@example.com',
          name: 'Test User',
          role: 'parent',
          created_at: 1645123456,
        },
      })
    );

    component.registerForm.controls['name'].setValue('Test User');
    component.registerForm.controls['email'].setValue('test@example.com');
    component.registerForm.controls['password'].setValue('password123');
    component.registerForm.controls['confirmPassword'].setValue('password123');

    // Act
    component.onSubmit();
    fixture.detectChanges();

    // Assert
    const successElement =
      fixture.nativeElement.querySelector('.alert-success');
    expect(successElement.textContent).toContain('Registration successful');
  });

  it('should display validation errors when form is submitted with errors', () => {
    // Arrange
    component.registerForm.controls['name'].setValue('Test User');
    component.registerForm.controls['email'].setValue('invalid-email');

    // Act
    component.onSubmit();
    fixture.detectChanges();

    // Assert
    const emailError = fixture.nativeElement.querySelector('.invalid-feedback');
    expect(emailError).toBeTruthy();
    expect(emailError.textContent).toContain(
      'Please enter a valid email address'
    );
  });
});
