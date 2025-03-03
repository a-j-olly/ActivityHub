import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ChallengeListComponent } from './challenge-list.component';

describe('ChallengeListComponent', () => {
  let component: ChallengeListComponent;
  let fixture: ComponentFixture<ChallengeListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ChallengeListComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ChallengeListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render the challenges heading', () => {
    const compiled = fixture.nativeElement;
    expect(compiled.querySelector('h2').textContent).toContain('Challenges');
  });

  it('should display placeholder text about future implementation', () => {
    const compiled = fixture.nativeElement;
    const paragraphs = compiled.querySelectorAll('p');
    
    // Check content of paragraphs
    expect(paragraphs.length).toBe(2);
    expect(paragraphs[0].textContent).toContain('This component will display a list of available challenges');
    expect(paragraphs[1].textContent).toContain('It will be fully implemented in future development stages');
  });
});
