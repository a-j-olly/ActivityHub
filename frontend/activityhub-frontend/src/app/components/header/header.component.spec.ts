import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { By } from '@angular/platform-browser';
import { BehaviorSubject } from 'rxjs';

import { HeaderComponent } from './header.component';
import { AuthService, User } from '../../services/auth.service';

describe('HeaderComponent', () => {
  let component: HeaderComponent;
  let fixture: ComponentFixture<HeaderComponent>;
  let authServiceSpy: jest.SpyInstance;
  let currentUserSubject: BehaviorSubject<User | null>;
  let mockAuthService: Partial<AuthService>;

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
      declarations: [HeaderComponent],
      imports: [RouterTestingModule],
      providers: [
        { provide: AuthService, useValue: mockAuthService }
      ]
    }).compileComponents();

    authServiceSpy = jest.spyOn(mockAuthService, 'logout');
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(HeaderComponent);
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
  it('should display user name when user is logged in', () => {
    // Arrange
    currentUserSubject.next(parentUser);
    fixture.detectChanges();
    
    // Assert
    const userInfo = fixture.nativeElement.querySelector('.user-info');
    expect(userInfo.textContent).toContain('Parent User');
  });

  it('should show login/register buttons when no user is logged in', () => {
    // Arrange
    currentUserSubject.next(null);
    fixture.detectChanges();
    
    // Assert
    const loginButton = fixture.debugElement.query(By.css('a.btn-primary'));
    const registerButton = fixture.debugElement.query(By.css('a.btn-outline'));
    
    expect(loginButton).toBeTruthy();
    expect(loginButton.nativeElement.textContent).toContain('Login');
    expect(registerButton).toBeTruthy();
    expect(registerButton.nativeElement.textContent).toContain('Register');
  });

  it('should show parent-specific links when parent is logged in', () => {
    // Arrange
    currentUserSubject.next(parentUser);
    fixture.detectChanges();
    
    // Assert
    const navLinks = fixture.debugElement.queryAll(By.css('.nav-links a'));
    // Extract only the path portion from the URLs
    const linkPaths = navLinks.map(link => {
      const href = link.properties['href'];
      return href.replace(/^http:\/\/[^\/]+/, '');
    });
    
    expect(linkPaths).toContain('/children');
    expect(linkPaths).not.toContain('/submissions');
  });

  it('should show child-specific links when child is logged in', () => {
    // Arrange
    currentUserSubject.next(childUser);
    fixture.detectChanges();
    
    // Assert
    const navLinks = fixture.debugElement.queryAll(By.css('.nav-links a'));
    // Extract only the path portion from the URLs
    const linkPaths = navLinks.map(link => {
      const href = link.properties['href'];
      return href.replace(/^http:\/\/[^\/]+/, '');
    });
    
    expect(linkPaths).toContain('/submissions');
    expect(linkPaths).not.toContain('/children');
  });

  it('should show logout button when user is logged in', () => {
    // Arrange
    currentUserSubject.next(parentUser);
    fixture.detectChanges();
    
    // Assert
    const logoutButton = fixture.debugElement.query(By.css('button.btn-outline'));
    expect(logoutButton).toBeTruthy();
    expect(logoutButton.nativeElement.textContent).toContain('Logout');
  });
});