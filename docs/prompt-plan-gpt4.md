Prompt 1: Project Setup & Environment Configuration

# Prompt 1: Project Setup & Environment Configuration

You are tasked with setting up the initial project structure for ActivityHub. Create a new repository that will contain two main folders: "frontend" for the Angular application and "backend" for the Flask API. Within each folder, initialize the appropriate project scaffolding.

For the backend:

- Create a Python virtual environment.
- Set up a minimal Flask project with a basic "app.py" file that includes a simple “Hello World” endpoint.
- Add a requirements.txt with Flask and boto3.

For the frontend:

- Use Angular CLI to generate a new Angular project.
- Create a basic routing module and a simple home component.

Finally, include a README.md at the repository root with an overview of the ActivityHub project. This README should briefly describe the purpose, key features, and technology stack.

Ensure that the structure is clean and that each piece is wired together (e.g., the Angular project is in its own folder and the Flask app can be run from the backend folder).

Once complete, verify that you can run the Flask app locally and the Angular app using “ng serve”.

Prompt 2: AWS Infrastructure Setup with Terraform

# Prompt 2: AWS Infrastructure Setup with Terraform

Next, set up the AWS infrastructure using Terraform. Write Terraform configuration files that will provision the following resources:

- AWS Cognito User Pool (for authentication).
- A DynamoDB table using a single-table design (named "ActivityHub").
- Two S3 buckets: one for raw media ("activityhub-media-raw") and one for processed media ("activityhub-media-processed").
- An AWS API Gateway that will later integrate with your Lambda functions.
- (Optional for now) A placeholder for an AWS Lambda function.

Include any necessary IAM roles and policies for your Lambda functions and API Gateway to interact with DynamoDB and S3. Also, structure the Terraform code to support both staging and production environments (for example, using workspaces or separate variable files).

Make sure to wire the resources so that later on, when you deploy your backend code, it can correctly interact with these AWS services.

Prompt 3: Flask Back-End Initialization

# Prompt 3: Flask Back-End Initialization

Now, focus on the backend. Expand your minimal Flask app into a structured API application. Create a Flask project with the following features:

- Organize the project with a clear structure (e.g., separate folders for routes, models, and utilities).
- Implement API endpoints for user registration and login:
  - POST /register: Accept user details and create a new user.
  - POST /login: Validate credentials and return a JWT token.
- Set up basic error handling for 400, 401, and 500 HTTP statuses.
- Integrate a configuration file (config.py) that will later include settings for AWS services, JWT secret, etc.

Ensure the endpoints are wired together in the main application entry point, so that when the app is started, these routes are available.

Prompt 4: DynamoDB Integration in Flask

# Prompt 4: DynamoDB Integration in Flask

Extend your Flask backend by integrating with DynamoDB. Using boto3, implement the following:

- A module to abstract DynamoDB operations (e.g., a "database.py" utility) that provides functions for CRUD operations on your single-table design.
- Enhance the user registration endpoint (/register) to store new user data in DynamoDB using the appropriate partition key (e.g., USER#<userId>) and sort key.
- Create a GET /user/<userId> endpoint that retrieves user profile details from DynamoDB.

Wire these new functionalities into your Flask app and test that the endpoints correctly interact with a local or test instance of DynamoDB.

Prompt 5: Angular Front-End Initialization

# Prompt 5: Angular Front-End Initialization

Now, develop the initial front-end components in your Angular project:

- Create a login component with a simple form (email and password) and a registration component.
- Set up an Angular service (e.g., AuthService) that will handle API calls for registration and login.
- Configure Angular routing so that users can navigate between the login, registration, and a basic home/dashboard component.
- Wire the login form to call the backend login endpoint and handle the returned JWT token (store it securely, e.g., in memory or in HTTPOnly cookies if possible).

Ensure that each Angular component is connected to the AuthService, and that navigation between pages works properly.

# Prompt 5.1: Angular Unit Tests

Before continuing with development, please produce unit tests for the Angular frontend. Output ".spec" files for each of the classes in the application. Please follow Angular best practices in unit testing.:

- Use Karma/Jasmine and the TestBed
- Use Shallow Testing When Possible
- Mock Child Components and Dependencies
- Test Reactive Forms
- Follow the Arrange-Act-Assert Pattern
- Test DOM Interactions Carefully
- Reuse When Possible

Do not produce E2E tests at this stage.

# Prompt 5.2: Python Unit Tests

Produce unit tests for the flask (v2.3.x) backend and output them as files. Use pytest and follow best practices.

Prompt 6: AWS Cognito Integration for Authentication

# Prompt 6: AWS Cognito Integration for Authentication

Integrate AWS Cognito into both your Flask backend and Angular front-end for user authentication:

For the backend:

- Implement a middleware (or decorator) that verifies the JWT tokens issued by AWS Cognito on protected endpoints.
- Modify the /login endpoint (if needed) so that it can validate the user against Cognito and issue/verify tokens accordingly.

For the frontend:

- Use AWS Amplify (or the AWS SDK for JavaScript) to connect to your Cognito User Pool.
- Update your AuthService to leverage AWS Cognito for registration and login, ensuring that the JWT token is properly managed.
- Ensure that once logged in, the Angular app stores the token securely and includes it in subsequent API calls.

Wire these changes together so that both the front-end and back-end share the same authentication mechanism.

Prompt 7: Challenge & Submission Endpoints in Flask

# Prompt 7: Challenge & Submission Endpoints in Flask

Expand your Flask backend by adding endpoints for the core features of ActivityHub:

- Create endpoints to handle challenges:
  - GET /challenges: Retrieve a list of active challenges.
  - GET /challenges/<challengeId>: Retrieve details of a specific challenge.
  - POST /challenges/<challengeId>/vote: Allow users to vote on a challenge.
- Create endpoints to handle submissions:
  - POST /challenges/<challengeId>/submit: Accept a submission (photo/video) for a challenge.
  - GET /submissions/<submissionId>: Retrieve submission details.
  - GET /users/<userId>/submissions: Retrieve all submissions by a user.
- Add endpoints for parental controls:
  - POST /parents/<parentId>/approve: Approve a child’s submission.
  - POST /parents/<parentId>/reject: Reject a submission.
  - POST /parents/<parentId>/setLimits: Set activity limits for a child.
  - GET /parents/<parentId>/activity: Retrieve a child’s activity history.

Ensure that these endpoints are wired to use the authentication middleware from the previous step and that they interact with DynamoDB appropriately.

Prompt 8: Media Processing & Content Moderation Integration

# Prompt 8: Media Processing & Content Moderation Integration

Develop the media processing pipeline that will handle user-submitted photos/videos:

- Create an AWS Lambda function (in Python) that is triggered by an S3 event when a new file is uploaded to the "activityhub-media-raw" bucket.
- Integrate Amazon Rekognition within this Lambda to scan the media for inappropriate content.
- Use OpenCV (packaged as a Lambda layer) within the same Lambda to perform face detection and blurring.
- Once processed, save the media to the "activityhub-media-processed" bucket.
- Ensure that the Lambda function communicates the status back to your Flask backend (for example, by updating the submission record in DynamoDB).

Wire the Lambda function with S3 event notifications and test the entire moderation pipeline with a sample media file.

Prompt 9: Leaderboard & Real-Time Updates using Redis

# Prompt 9: Leaderboard & Real-Time Updates using Redis

Implement the leaderboard functionality using Redis for real-time performance:

- In your Flask backend, create endpoints for:
  - GET /leaderboards/<challengeId>: Retrieve the leaderboard for a specific challenge.
  - GET /leaderboards/overall: Retrieve the overall leaderboard across challenges.
- Use Redis sorted sets to maintain ranking data. Write helper functions that update a challenge’s leaderboard whenever a submission is approved or a vote is cast.
- Wire the Redis integration so that leaderboard data is updated in real time and falls back to DynamoDB data if Redis is unavailable.

Ensure these endpoints are connected to the existing user and challenge endpoints.

Prompt 10: Integration Testing and Final Wiring

# Prompt 10: Integration Testing and Final Wiring

Bring all the pieces together and ensure the system works as a cohesive whole:

- Write integration tests (using pytest for Flask and Postman/Insomnia for API endpoints) that simulate a complete user workflow: registration, login, challenge submission, moderation, parental approval, and leaderboard updates.
- Create end-to-end tests using Cypress for the Angular front-end. These tests should simulate a user logging in, submitting a challenge, and viewing the updated leaderboard.
- Wire the entire deployment pipeline using AWS SAM for Lambda functions and Terraform for infrastructure deployment. Ensure that environment variables and configurations are correctly passed from your local setup to the cloud environment.
- Document the complete flow in your README and include troubleshooting steps for common issues (e.g., authentication failures, S3 event trigger problems).

The final prompt should ensure that all components (frontend, backend, AWS services) are integrated and tested together, forming a working version of ActivityHub.
