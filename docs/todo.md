# ActivityHub Project To-Do Checklist

## 1. Project Setup & Environment Configuration

- [x] **Repository Structure**
  - [x] Create a new repository.
  - [x] Create two main folders: `/frontend` and `/backend`.
  - [x] Add a root-level `README.md` with project overview and tech stack.
- [x] **Backend Initial Setup**
  - [x] Set up a Python virtual environment.
  - [x] Initialize a minimal Flask project with an `app.py` file.
  - [x] Implement a “Hello World” endpoint in Flask.
  - [x] Create a `requirements.txt` including Flask and boto3.
- [x] **Frontend Initial Setup**
  - [x] Scaffold a new Angular project using Angular CLI inside `/frontend`.
  - [x] Set up Angular routing with a basic home component.
  - [x] Verify Angular app runs with `ng serve`.

## 2. AWS Infrastructure Setup with Terraform

- [x] **AWS Resources Provisioning**
  - [x] Write Terraform config to create an AWS Cognito User Pool.
  - [x] Provision a DynamoDB table (single-table design, name: `ActivityHub`).
  - [x] Create two S3 buckets:
    - [x] `activityhub-media-raw`
    - [x] `activityhub-media-processed`
  - [x] Set up AWS API Gateway for Lambda integration.
  - [x] (Optional) Add a placeholder for an AWS Lambda function.
- [x] **IAM & Environment Management**
  - [x] Create necessary IAM roles and policies for Lambda/API Gateway to access DynamoDB and S3.
  - [x] Configure Terraform for multiple environments (staging and production).

## 3. Flask Back-End Development

- [x] **Project Structure**
  - [x] Organize backend folders: routes, models, utilities.
  - [x] Create a `config.py` for environment variables and AWS settings.
- [x] **User Management Endpoints**
  - [x] Implement `POST /register` for user registration.
  - [x] Implement `POST /login` for user authentication.
  - [x] Create a JWT token issuance mechanism.
- [x] **Error Handling**
  - [x] Add error handling for 400, 401, 403, 404, and 500 status codes.
- [x] **Wiring**
  - [x] Wire all routes in the main app entry point.

## 4. DynamoDB Integration in Flask

- [x] **DynamoDB Utility Module**
  - [x] Create a module (e.g., `database.py`) for CRUD operations.
- [x] **Enhance Endpoints**
  - [x] Update `/register` to save new user data in DynamoDB.
  - [x] Implement `GET /user/<userId>` to retrieve user profiles from DynamoDB.

## 5. Angular Front-End Development

- [x] **Core Components**
  - [x] Create a login component with email/password form.
  - [x] Create a registration component.
  - [x] Create a home/dashboard component.
- [x] **Service Integration**
  - [x] Develop an `AuthService` to handle registration and login API calls.
- [x] **Routing**
  - [x] Set up Angular routing for navigation between login, registration, and home.
- [x] **JWT Handling**
  - [x] Integrate login form to call backend `/login` endpoint.
  - [x] Securely store and manage JWT tokens.

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
