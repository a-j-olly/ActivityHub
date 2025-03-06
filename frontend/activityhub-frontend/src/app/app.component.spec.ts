import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { Component } from '@angular/core';
import { AppComponent } from './app.component';

// Create stub for HeaderComponent
@Component({
  selector: 'app-header',
  template: '<div>Header Stub</div>',
  standalone: false,
})
class HeaderStubComponent {}

describe('AppComponent', () => {
  let fixture: ComponentFixture<AppComponent>;
  let component: AppComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RouterTestingModule],
      declarations: [
        AppComponent,
        HeaderStubComponent, // Use stub instead of real component
      ],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AppComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create the app', () => {
    expect(component).toBeTruthy();
  });

  it('should have as title "ActivityHub"', () => {
    expect(component.title).toEqual('ActivityHub');
  });

  it('should render header component', () => {
    const compiled = fixture.nativeElement;
    expect(compiled.querySelector('app-header')).toBeTruthy();
  });

  it('should render router outlet', () => {
    const compiled = fixture.nativeElement;
    expect(compiled.querySelector('router-outlet')).toBeTruthy();
  });

  it('should render footer with copyright information', () => {
    const compiled = fixture.nativeElement;
    const footerElement = compiled.querySelector('.app-footer');
    expect(footerElement).toBeTruthy();
    expect(footerElement.textContent).toContain('ActivityHub');
    expect(footerElement.textContent).toContain('2025');
  });
});