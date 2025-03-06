export const environment = {
  production: true,
  apiUrl: '/api',
  cognitoConfig: {
    region: 'us-west-2',
    userPoolId: 'us-west-2_xxxxxxxx',  // Replace with your Cognito User Pool ID
    userPoolWebClientId: 'xxxxxxxxxxxxxxxxxxxxxxxxxx'  // Replace with your App Client ID
  }
};