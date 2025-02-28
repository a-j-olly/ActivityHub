# ActivityHub

## Overview

ActivityHub is a gamified web application designed to encourage children to engage in outdoor activities by participating in skill-based challenges. The app provides a platform where children can submit proof of completed activities, view leaderboards, and earn recognition for their accomplishments, all within a safe environment supervised by parents.

## Key Features

- **Skill-based Challenges**: Various outdoor activities with different difficulty levels
- **Challenge Submissions**: Users can submit photos/videos as proof of completing challenges
- **Leaderboards**: Real-time rankings for each challenge and overall participation
- **Parental Controls**: Parents can approve/reject submissions and monitor activity
- **Safety Features**: Comprehensive safety guidelines and risk management

## Technology Stack

### Frontend

- **Framework**: Angular
- **Hosting**: AWS Amplify
- **Testing**: Jasmine and Cypress

### Backend

- **Framework**: Flask (Python)
- **Runtime**: AWS Lambda
- **API Gateway**: RESTful API

### Database

- **Primary Database**: DynamoDB (single-table design)
- **Cache**: Redis (ElastiCache) for leaderboards

### Storage

- **Media Storage**: Amazon S3

### Authentication

- **Service**: AWS Cognito

### Content Moderation & Safety

- **Media Processing**: Amazon Rekognition for content moderation
- **Face Blurring**: OpenCV via Lambda Layer

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+ and npm
- AWS CLI configured with appropriate permissions
- Terraform for infrastructure deployment

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py  # Runs the Flask development server
Frontend Setup
bash
```

### Frontend Setup

```bash
cd frontend/activityhub-frontend
npm install
ng serve  # Launches the development server at http://localhost:4200
```

### Project Structure

- /backend: Flask API and AWS Lambda functions
- /frontend: Angular web application
- /terraform: Infrastructure as Code configurations (to be added)

### Development Roadmap

1. User authentication and registration
2. Challenge creation and management
3. Challenge submissions and media processing
4. Leaderboards and social features
5. Parental controls and safety features
6. Deployment and production optimizations

### Infrastructure Setup

The AWS infrastructure for ActivityHub is managed using Terraform. The infrastructure includes:

#### AWS Resources

- **AWS Cognito User Pool**: For user authentication and authorization
- **DynamoDB Table**: Single-table design named "ActivityHub" for storing application data
- **S3 Buckets**:
  - `activityhub-media-raw`: For storing raw media uploads (deleted after 24 hours)
  - `activityhub-media-processed`: For storing processed media (with face blurring and moderation)
- **API Gateway**: RESTful API for frontend communication
- **AWS Lambda**: Serverless functions for backend processing
- **IAM Roles and Policies**: For secure resource access

#### Environment Management

The infrastructure is configured to support both staging and production environments:

- **Staging**: Used for development and testing
- **Production**: Used for the live application

#### Terraform Usage

```bash
cd terraform

# Initialize Terraform
terraform init

# For staging environment
terraform workspace select staging
terraform apply -var-file=environments/staging.tfvars

# For production environment
terraform workspace select production
terraform apply -var-file=environments/production.tfvars
```

For more details, see the [terraform/README.md](terraform/README.md) file.

### License

[License information to be added]
