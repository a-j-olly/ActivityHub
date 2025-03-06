import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { RouterTestingModule } from '@angular/router/testing';
import { Router } from '@angular/router';
import { of, throwError } from 'rxjs';

import { RegisterComponent } from './register.component';
import { AuthService } from '../../services/auth.service';
import { LoginComponent } from '../login/login.component';

describe('RegisterComponent', () => {
  let component: RegisterComponent;
  let fixture: ComponentFixture<RegisterComponent>;
  let mockAuthService: Partial<AuthService>;
  let router: Router;

  beforeEach(async () => {
    // Create AuthService mock with the methods we'll use
    mockAuthService = {
      register: jest.fn(),
      isLoggedIn: jest.fn().mockReturnValue(false)
    };

    await TestBed.configureTestingModule({
      declarations: [RegisterComponent],
      imports: [
        ReactiveFormsModule, 
        // Add mock routes to handle navigation
        RouterTestingModule.withRoutes([
          { path: 'login', component: {} as any }, // Mock component
          { path: 'home', component: {} as any }   // Mock component
        ])
      ],
      providers: [{ provide: AuthService, useValue: mockAuthService }],
    }).compileComponents();

    router = TestBed.inject(Router);
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(RegisterComponent);
    component = fixture.componentInstance;
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
    (mockAuthService.isLoggedIn as jest.Mock).mockReturnValue(true);
    const navigateSpy = jest.spyOn(router, 'navigate');

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
    expect(component.submitted).toBe(true);
    expect(mockAuthService.register).not.toHaveBeenCalled();
  });

  it('should call auth service register when form is valid', () => {
    // Arrange
    (mockAuthService.register as jest.Mock).mockReturnValue(
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
    expect(mockAuthService.register).toHaveBeenCalledWith(
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
    (mockAuthService.register as jest.Mock).mockReturnValue(
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

    const navigateSpy = jest.spyOn(router, 'navigate');

    component.registerForm.controls['name'].setValue('Test User');
    component.registerForm.controls['email'].setValue('test@example.com');
    component.registerForm.controls['password'].setValue('password123');
    component.registerForm.controls['confirmPassword'].setValue('password123');

    // Act
    component.onSubmit();
    
    // Fast-forward the setTimeout
    tick(1500);

    // Assert
    expect(navigateSpy).toHaveBeenCalledWith(['/login']);
  }));

  it('should handle registration error', () => {
    // Arrange
    const errorMessage = 'Email already exists';
    (mockAuthService.register as jest.Mock).mockReturnValue(throwError(() => errorMessage));

    component.registerForm.controls['name'].setValue('Test User');
    component.registerForm.controls['email'].setValue('test@example.com');
    component.registerForm.controls['password'].setValue('password123');
    component.registerForm.controls['confirmPassword'].setValue('password123');

    // Act
    component.onSubmit();

    // Assert
    expect(component.error).toBe(errorMessage);
    expect(component.success).toBe('');
    expect(component.loading).toBe(false);
  });

  // DOM Testing
  it('should display success message when registration succeeds', () => {
    // Arrange
    (mockAuthService.register as jest.Mock).mockReturnValue(
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
    const successElement = fixture.nativeElement.querySelector('.alert-success');
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