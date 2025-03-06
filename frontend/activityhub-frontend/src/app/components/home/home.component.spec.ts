import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject } from 'rxjs';

import { HomeComponent } from './home.component';
import { AuthService, User } from '../../services/auth.service';

describe('HomeComponent', () => {
  let component: HomeComponent;
  let fixture: ComponentFixture<HomeComponent>;
  let mockAuthService: Partial<AuthService>;
  let currentUserSubject: BehaviorSubject<User | null>;

  // Sample user data
  const parentUser: User = {
    user_id: '123',
    email: 'parent@example.com',
    name: 'Parent User',
    role: 'parent',
    created_at: 1645123456
  };

  const childUser: User = {
    user_id: '456',
    email: 'child@example.com',
    name: 'Child User',
    role: 'child',
    created_at: 1645123456
  };

  beforeEach(async () => {
    // Create a mock currentUser observable
    currentUserSubject = new BehaviorSubject<User | null>(null);
    
    // Create AuthService mock with the methods we'll use
    mockAuthService = {
      logout: jest.fn(),
      currentUser: currentUserSubject.asObservable()
    };

    await TestBed.configureTestingModule({
      declarations: [HomeComponent],
      providers: [
        { provide: AuthService, useValue: mockAuthService }
      ]
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(HomeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should update currentUser when auth service emits a new user', () => {
    // Arrange & Act
    currentUserSubject.next(parentUser);
    fixture.detectChanges();
    
    // Assert
    expect(component.currentUser).toEqual(parentUser);
  });

  it('should call logout method in auth service when logout is called', () => {
    // Arrange
    currentUserSubject.next(parentUser);
    fixture.detectChanges();
    
    // Act
    component.logout();
    
    // Assert
    expect(mockAuthService.logout).toHaveBeenCalled();
  });

  // DOM Testing
  it('should display parent-specific content when user is a parent', () => {
    // Arrange
    currentUserSubject.next(parentUser);
    fixture.detectChanges();
    
    // Assert
    const parentDashboard = fixture.nativeElement.querySelector('h3');
    expect(parentDashboard.textContent).toContain('Parent Dashboard');
  });

  it('should display child-specific content when user is a child', () => {
    // Arrange
    currentUserSubject.next(childUser);
    fixture.detectChanges();
    
    // Assert
    const childDashboard = fixture.nativeElement.querySelector('h3');
    expect(childDashboard.textContent).toContain('Child Dashboard');
  });

  it('should display warning message when no user is logged in', () => {
    // Arrange
    currentUserSubject.next(null);
    fixture.detectChanges();
    
    // Assert
    const warningMessage = fixture.nativeElement.querySelector('.alert-warning');
    expect(warningMessage).toBeTruthy();
    expect(warningMessage.textContent).toContain('You are not logged in');
  });

  it('should show logout button when user is logged in', () => {
    // Arrange
    currentUserSubject.next(parentUser);
    fixture.detectChanges();
    
    // Assert
    const logoutButton = fixture.nativeElement.querySelector('.btn-danger');
    expect(logoutButton).toBeTruthy();
    expect(logoutButton.textContent).toContain('Logout');
  });

  it('should not show logout button when no user is logged in', () => {
    // Arrange
    currentUserSubject.next(null);
    fixture.detectChanges();
    
    // Assert
    const logoutButton = fixture.nativeElement.querySelector('.btn-danger');
    expect(logoutButton).toBeFalsy();
  });
});