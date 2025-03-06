// src/app/services/amplify.service.ts
import { Injectable } from '@angular/core';
import { Amplify } from 'aws-amplify';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AmplifyService {
  constructor() {
    this.configureAmplify();
  }

  private configureAmplify(): void {
    Amplify.configure({
      Auth: {
        Cognito: {
          userPoolId: environment.cognitoConfig.userPoolId,
          userPoolClientId: environment.cognitoConfig.userPoolWebClientId,
          loginWith: {
            email: true
          }
        }
      }
    });
  }
}