# ActivityHub Project To-Do Checklist

## 1. Project Setup & Environment Configuration

- [*] **Repository Structure**
  - [*] Create a new repository.
  - [*] Create two main folders: `/frontend` and `/backend`.
  - [*] Add a root-level `README.md` with project overview and tech stack.
- [*] **Backend Initial Setup**
  - [*] Set up a Python virtual environment.
  - [*] Initialize a minimal Flask project with an `app.py` file.
  - [*] Implement a “Hello World” endpoint in Flask.
  - [*] Create a `requirements.txt` including Flask and boto3.
- [*] **Frontend Initial Setup**
  - [*] Scaffold a new Angular project using Angular CLI inside `/frontend`.
  - [*] Set up Angular routing with a basic home component.
  - [*] Verify Angular app runs with `ng serve`.

## 2. AWS Infrastructure Setup with Terraform

- [ ] **AWS Resources Provisioning**
  - [ ] Write Terraform config to create an AWS Cognito User Pool.
  - [ ] Provision a DynamoDB table (single-table design, name: `ActivityHub`).
  - [ ] Create two S3 buckets:
    - [ ] `activityhub-media-raw`
    - [ ] `activityhub-media-processed`
  - [ ] Set up AWS API Gateway for Lambda integration.
  - [ ] (Optional) Add a placeholder for an AWS Lambda function.
- [ ] **IAM & Environment Management**
  - [ ] Create necessary IAM roles and policies for Lambda/API Gateway to access DynamoDB and S3.
  - [ ] Configure Terraform for multiple environments (staging and production).

## 3. Flask Back-End Development

- [ ] **Project Structure**
  - [ ] Organize backend folders: routes, models, utilities.
  - [ ] Create a `config.py` for environment variables and AWS settings.
- [ ] **User Management Endpoints**
  - [ ] Implement `POST /register` for user registration.
  - [ ] Implement `POST /login` for user authentication.
  - [ ] Create a JWT token issuance mechanism.
- [ ] **Error Handling**
  - [ ] Add error handling for 400, 401, 403, 404, and 500 status codes.
- [ ] **Wiring**
  - [ ] Wire all routes in the main app entry point.

## 4. DynamoDB Integration in Flask

- [ ] **DynamoDB Utility Module**
  - [ ] Create a module (e.g., `database.py`) for CRUD operations.
- [ ] **Enhance Endpoints**
  - [ ] Update `/register` to save new user data in DynamoDB.
  - [ ] Implement `GET /user/<userId>` to retrieve user profiles from DynamoDB.
- [ ] **Testing**
  - [ ] Test endpoints with a local/test DynamoDB instance.

## 5. Angular Front-End Development

- [ ] **Core Components**
  - [ ] Create a login component with email/password form.
  - [ ] Create a registration component.
  - [ ] Create a home/dashboard component.
- [ ] **Service Integration**
  - [ ] Develop an `AuthService` to handle registration and login API calls.
- [ ] **Routing**
  - [ ] Set up Angular routing for navigation between login, registration, and home.
- [ ] **JWT Handling**
  - [ ] Integrate login form to call backend `/login` endpoint.
  - [ ] Securely store and manage JWT tokens.

## 6. AWS Cognito Integration for Authentication

- [ ] **Backend Integration**
  - [ ] Implement middleware/decorator in Flask to validate AWS Cognito JWT tokens.
  - [ ] Modify `/login` to work with Cognito (if required).
- [ ] **Frontend Integration**
  - [ ] Integrate AWS Amplify or AWS SDK for JS to connect with Cognito.
  - [ ] Update `AuthService` to use Cognito for authentication.
  - [ ] Ensure secure storage and transmission of JWT tokens.

## 7. Challenge & Submission Endpoints in Flask

- [ ] **Challenge Endpoints**
  - [ ] Implement `GET /challenges` for active challenges.
  - [ ] Implement `GET /challenges/<challengeId>` for challenge details.
  - [ ] Implement `POST /challenges/<challengeId>/vote` for challenge voting.
- [ ] **Submission Endpoints**
  - [ ] Implement `POST /challenges/<challengeId>/submit` for challenge submissions.
  - [ ] Implement `GET /submissions/<submissionId>` for submission details.
  - [ ] Implement `GET /users/<userId>/submissions` for listing user submissions.
- [ ] **Parental Controls Endpoints**
  - [ ] Implement `POST /parents/<parentId>/approve` for submission approval.
  - [ ] Implement `POST /parents/<parentId>/reject` for submission rejection.
  - [ ] Implement `POST /parents/<parentId>/setLimits` for activity limit setting.
  - [ ] Implement `GET /parents/<parentId>/activity` for viewing child activity.
- [ ] **Integration**
  - [ ] Ensure all endpoints are protected by authentication middleware.
  - [ ] Test API endpoints for proper integration with DynamoDB.

## 8. Media Processing & Content Moderation Pipeline

- [ ] **AWS Lambda Function**
  - [ ] Create a new Lambda function (Python) triggered by S3 events (new file upload to `activityhub-media-raw`).
- [ ] **Content Moderation**
  - [ ] Integrate Amazon Rekognition for scanning media content.
- [ ] **Face Blurring**
  - [ ] Integrate OpenCV (via Lambda layer) to detect and blur faces.
- [ ] **Media Handling**
  - [ ] Save processed media to `activityhub-media-processed`.
  - [ ] Update submission records in DynamoDB to reflect processing status.
- [ ] **Testing**
  - [ ] Test the complete media pipeline with sample media files.

## 9. Leaderboard & Real-Time Updates using Redis

- [ ] **Redis Integration**
  - [ ] Set up Redis (ElastiCache) and define sorted sets for leaderboards.
- [ ] **Endpoint Development**
  - [ ] Implement `GET /leaderboards/<challengeId>` for challenge-specific leaderboards.
  - [ ] Implement `GET /leaderboards/overall` for overall leaderboard.
- [ ] **Helper Functions**
  - [ ] Write helper functions to update leaderboard data upon submission approval/votes.
- [ ] **Fallback Mechanism**
  - [ ] Implement fallback to DynamoDB if Redis is unavailable.
- [ ] **Testing**
  - [ ] Verify real-time updates with simulated leaderboard events.

## 10. Integration Testing and Final Wiring

- [ ] **Backend Integration Tests**
  - [ ] Write unit tests using pytest for Flask endpoints.
  - [ ] Use Postman/Insomnia to manually test API workflows.
- [ ] **Front-End End-to-End Tests**
  - [ ] Develop Cypress tests simulating complete user workflows.
- [ ] **CI/CD Pipeline**
  - [ ] Set up CI/CD pipelines for Angular and Flask deployments.
- [ ] **Deployment Integration**
  - [ ] Use AWS SAM to package and deploy Lambda functions.
  - [ ] Use Terraform to deploy infrastructure.
  - [ ] Ensure environment variables and configurations are correctly passed.
- [ ] **Documentation**
  - [ ] Update the README with complete system flow and troubleshooting steps.

## 11. Security & Compliance

- [ ] **Authentication & Authorization**
  - [ ] Ensure AWS Cognito is properly integrated.
  - [ ] Enforce RBAC in the backend.
- [ ] **Data Encryption**
  - [ ] Enable encryption at rest for DynamoDB, S3, and Redis.
  - [ ] Ensure HTTPS/TLS is used for all data transmission.
- [ ] **Logging & Monitoring**
  - [ ] Set up AWS CloudTrail and AWS Config.
  - [ ] Log API calls and monitor resource changes.
- [ ] **COPPA/GDPR-K Compliance**
  - [ ] Implement age gate and parental consent mechanisms.
  - [ ] Set up data retention policies and deletion triggers.

## 12. Final Review & Accessibility

- [ ] **Accessibility Auditing**
  - [ ] Audit the Angular app for WCAG 2.1 Level AA compliance.
  - [ ] Run accessibility tests and document any issues.
- [ ] **Overall Integration Review**
  - [ ] Verify that all components (frontend, backend, AWS services) are fully integrated.
  - [ ] Conduct end-to-end user journey tests.
  - [ ] Update documentation and check for orphaned code or features.
