import { TestBed } from '@angular/core/testing';
import { AmplifyService } from './amplify.service';
import { Amplify } from 'aws-amplify';
import { environment } from '../../environments/environment';

describe('AmplifyService', () => {
  let service: AmplifyService;

  beforeEach(() => {
    // Spy on the Amplify.configure method before each test
    jest.spyOn(Amplify, 'configure');
    
    TestBed.configureTestingModule({
      providers: [AmplifyService]
    });
    
    service = TestBed.inject(AmplifyService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
  
  it('should configure Amplify with the correct parameters', () => {
    // Assert that configure was called
    expect(Amplify.configure).toHaveBeenCalled();
    
    // Get the first call arguments
    const configArg = (Amplify.configure as jest.Mock).mock.calls[0][0];
    
    // Check structure without using objectContaining
    expect(configArg).toBeTruthy();
    expect(configArg.Auth).toBeTruthy();
    expect(configArg.Auth.Cognito).toBeTruthy();
    expect(configArg.Auth.Cognito.userPoolId).toBe(environment.cognitoConfig.userPoolId);
    expect(configArg.Auth.Cognito.userPoolClientId).toBe(environment.cognitoConfig.userPoolWebClientId);
  });
});