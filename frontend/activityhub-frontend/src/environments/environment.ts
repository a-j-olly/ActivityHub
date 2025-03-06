export const environment = {
  production: false,
  apiUrl: 'http://localhost:5000/api',
  cognitoConfig: {
    region: 'eu-west-2',
    userPoolId: '',  // Replace with your Cognito User Pool ID
    userPoolWebClientId: ''  // Replace with your App Client ID
  }
};