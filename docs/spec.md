# ActivityHub: Streamlined Developer Specification

---

## 1. Overview

**ActivityHub** is a gamified web application designed to encourage children to engage in outdoor activities by participating in skill-based challenges. The app includes features like challenge submissions, leaderboards, and parental controls, with a focus on reducing screen time, promoting physical activity, and ensuring user safety.

---

## 2. Key Features

1. **User Roles:**

   - **Child:** Can submit challenges, view leaderboards, and participate in activities.
   - **Parent:** Can approve/reject submissions, monitor their child’s activity, and set safety limits.
   - **Admin:** Can create/update challenges and manage users.

2. **Challenges:**

   - Skill-based activities with varying difficulty levels (e.g., “100m Front Crawl”).
   - Challenges can be time-limited or always active.
   - Include safety guidelines and risk levels.

3. **Submissions:**

   - Users submit photos/videos as proof of completing a challenge.
   - Submissions are moderated for inappropriate content and have faces blurred.

4. **Leaderboards:**

   - Real-time rankings for each challenge and an overall leaderboard.
   - Rankings are based on challenge-specific metrics (e.g., time, distance).
   - Emphasize personal progress and participation over raw rankings.

5. **Parental Controls:**

   - Parents must approve submissions before they are counted.
   - Parents can view their child’s activity, set limits, and receive notifications for high-risk challenges.

6. **Notifications:**

   - Users receive notifications for submission approvals/rejections, challenge results, and safety reminders.

7. **Safety Features:**
   - Safety guidelines for each challenge.
   - Emergency contact information for high-risk activities.
   - Real-time notifications for parents during high-risk challenges.

---

## 3. Architecture

### Front-End

- **Framework:** Angular
- **Hosting:** AWS Amplify

### Back-End

- **Framework:** Flask (Python)
- **Runtime:** AWS Lambda
- **API Gateway:** RESTful API for front-end communication

### Database

- **Primary Database:** DynamoDB (single-table design)
- **Cache:** Redis (ElastiCache) for leaderboards and real-time updates

### Media Storage

- **Raw Media:** Amazon S3 (`activityhub-media-raw`)
- **Processed Media:** Amazon S3 (`activityhub-media-processed`)

### Authentication

- **Service:** AWS Cognito
- **Features:** User authentication, parental controls, JWT token issuance

### Content Moderation

- **Service:** Amazon Rekognition

### Face Blurring

- **Tool:** OpenCV (via Lambda Layer)

### Notifications

- **Service:** Amazon SNS

---

## 4. Data Handling

### DynamoDB Schema

- **Table Name:** `ActivityHub`
- **Primary Key:**
  - **Partition Key (PK):** Entity type + ID (e.g., `USER#123`, `CHALLENGE#456`)
  - **Sort Key (SK):** Descriptor (e.g., `PROFILE`, `SUBMISSION#789`)

### Redis Schema

- **Leaderboards:** `leaderboard:<ChallengeID>` (Sorted Set)
- **Votes:** `votes:<ChallengeID>` (Set)
- **User Submissions:** `user:<UserID>:submissions` (Set)
- **Notifications:** `notifications:<UserID>` (List)

### Media Storage

- **Raw Media:** Stored in `activityhub-media-raw` bucket (deleted after 24 hours).
- **Processed Media:** Stored in `activityhub-media-processed` bucket after moderation and face blurring.

---

## 5. API Endpoints

### User Management

- `POST /register` – Register a new user.
- `POST /login` – Authenticate a user and return a JWT token.
- `GET /user/{userId}` – Get user profile details.

### Challenges

- `GET /challenges` – Get a list of active challenges.
- `GET /challenges/{challengeId}` – Get details of a specific challenge.
- `POST /challenges/{challengeId}/vote` – Vote for a challenge.

### Submissions

- `POST /challenges/{challengeId}/submit` – Submit a challenge (with photo/video).
- `GET /submissions/{submissionId}` – Get details of a specific submission.
- `GET /users/{userId}/submissions` – Get all submissions by a user.

### Leaderboards

- `GET /leaderboards/{challengeId}` – Get the leaderboard for a specific challenge.
- `GET /leaderboards/overall` – Get the overall leaderboard across all challenges.

### Parental Controls

- `POST /parents/{parentId}/approve` – Approve a child’s submission.
- `POST /parents/{parentId}/reject` – Reject a child’s submission.
- `POST /parents/{parentId}/setLimits` – Set activity limits for a child.
- `GET /parents/{parentId}/activity` – Get a child’s activity history.

### Notifications

- `GET /notifications` – Get notifications for the user.

### Safety Features

- `GET /challenges/{challengeId}/safety` – Get safety guidelines for a challenge.
- `POST /parents/{parentId}/emergencyContacts` – Add emergency contact information.

---

## 6. Error Handling

### Common Errors

- **400 Bad Request:** Invalid input data.
- **401 Unauthorized:** Missing or invalid JWT token.
- **403 Forbidden:** User does not have permission to perform the action.
- **404 Not Found:** Resource not found (e.g., invalid challenge ID).
- **500 Internal Server Error:** Unexpected server error.

### Error Responses

- Example:
  ```json
  {
  	"error": "Unauthorized",
  	"message": "Missing or invalid JWT token.",
  	"statusCode": 401
  }
  ```

---

## 7. Testing Plan

### Unit Testing

- **Tools:** `pytest` for Python, `Jasmine` for Angular.
- **Coverage:**
  - Test Lambda functions for challenge submission, leaderboard updates, and face blurring.
  - Test Angular components for UI functionality.

### Integration Testing

- **Tools:** `Postman` or `Insomnia`.
- **Coverage:**
  - Test API endpoints for user registration, challenge submission, and leaderboard queries.
  - Verify integration between Lambda, DynamoDB, Redis, and S3.

### End-to-End Testing

- **Tools:** `Cypress` for Angular.
- **Coverage:**
  - Test user workflows (e.g., submitting a challenge, viewing leaderboards).
  - Verify parental controls (e.g., approving/rejecting submissions).

### Performance Testing

- **Tools:** `AWS Lambda PowerTools` for monitoring Lambda performance.
- **Coverage:**
  - Test leaderboard query performance with large datasets.
  - Test media processing performance (e.g., face blurring).

---

## 8. Deployment

### Infrastructure as Code (IaC)

- **Tool:** Terraform
- **Resources:**
  - Lambda functions, API Gateway, DynamoDB, Redis (ElastiCache), S3 buckets, Cognito.

### Lightweight Automation

- **Terraform Workspaces:** Manage staging and production environments.
- **AWS SAM CLI:** Package and deploy Lambda functions.

### Manual Deployment Steps

1. **Develop Locally:** Test Lambda functions using `sam local`.
2. **Package and Deploy:** Use `sam package` and Terraform to deploy to AWS.
3. **Test in Staging:** Verify functionality in the staging environment.
4. **Deploy to Production:** Repeat the deployment process for production.

---

## 9. Security & Compliance

### Authentication

- **AWS Cognito:** Handle user authentication and JWT token issuance.
- **JWT Token Security:**
  - Store tokens in HTTPOnly, Secure, SameSite cookies.
  - Use strict CORS policies to restrict front-end access.

### Authorization

- **RBAC:** Assign roles (Child, Parent, Admin) and enforce permissions.

### Data Encryption

- **At Rest:** Enable encryption for DynamoDB, S3, and Redis.
- **In Transit:** Use HTTPS for API Gateway and TLS for internal communication.

### Monitoring and Auditing

- **AWS CloudTrail:** Log all API calls and changes to resources.
- **AWS Config:** Monitor compliance with security policies.

### COPPA/GDPR-K Compliance

- **Age Gate:**
  - Users must input their birthdate during registration.
  - If the user is under 13, parental consent is required.
- **Parental Consent:**
  - Collect parental consent via email verification.
- **Data Retention Policy:**
  - Delete user data after 1 year of inactivity.
  - Notify users 30 days before deletion.

---

## 10. Media Handling

### Content Moderation

- **Amazon Rekognition:** Scan media for inappropriate content.
- **Appeal Process:**
  - Users can appeal rejected submissions via the app.
  - Admins review appeals and override rejections if necessary.

### Face Blurring

- **OpenCV:** Detect and blur faces in photos/videos.
- **Lambda Layer:** Package OpenCV and its dependencies for use in Lambda functions.

### Media Storage

- **Raw Media:** Stored in `activityhub-media-raw` bucket (deleted after 24 hours).
- **Processed Media:** Stored in `activityhub-media-processed` bucket after moderation and face blurring.

### Cost Management

- **Media Compression:** Reduce media resolution to 720p before storage.
- **S3 Lifecycle Policies:** Archive old media to Glacier after 30 days.

---

## 11. Redis Data Persistence

- **Redis Snapshots:** Enable daily snapshots for data persistence.
- **Fallback Mechanism:** Fetch leaderboard data from DynamoDB if Redis fails.

---

## 12. Accessibility

- **WCAG Compliance:** Audit the Angular app for **WCAG 2.1 Level AA** compliance.
- **Accessibility Testing:** Include accessibility testing in the testing plan.

---

## 13. Future Enhancements

1. **CI/CD Pipeline:** Automate testing and deployment using GitHub Actions or AWS CodePipeline.
2. **Advanced Analytics:** Track user engagement and challenge popularity.
3. **Social Features:** Allow users to share achievements and connect with friends.

---
