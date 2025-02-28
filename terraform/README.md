# ActivityHub Infrastructure

This directory contains Terraform configuration files for provisioning the AWS infrastructure required for ActivityHub.

## Infrastructure Components

- **AWS Cognito User Pool**: For user authentication and management
- **DynamoDB Table**: Single-table design for storing application data
- **S3 Buckets**: For storing raw and processed media files
- **API Gateway**: RESTful API for frontend communication
- **Lambda Functions**: For serverless backend processing
- **IAM Roles and Policies**: For secure resource access

## Directory Structure

```
terraform/
├── modules/
│   ├── cognito/
│   ├── dynamodb/
│   ├── s3/
│   ├── api_gateway/
│   ├── lambda/
│   └── iam/
├── environments/
│   ├── staging.tfvars
│   └── production.tfvars
├── main.tf
├── variables.tf
├── outputs.tf
└── providers.tf
```

## Usage

### Prerequisites

- Terraform CLI (v1.2.0+)
- AWS CLI configured with appropriate credentials
- (Optional) S3 bucket for Terraform state (recommended for team environments)

### Setting Up Remote State Storage (Optional but Recommended)

For team environments, it's recommended to use remote state storage. You can create the required resources using AWS CLI:

```bash
# Create S3 bucket for Terraform state
aws s3 mb s3://activityhub-terraform-state --region us-west-2

# Enable versioning on the bucket
aws s3api put-bucket-versioning --bucket activityhub-terraform-state --versioning-configuration Status=Enabled

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-west-2

# After creating these resources, uncomment and configure the backend "s3" block in providers.tf
```

### Initializing Terraform

```bash
# Initialize Terraform with local state
terraform init

# Or, after setting up remote state and uncommenting the backend block in providers.tf:
# Initialize with remote state
terraform init \
  -backend-config="bucket=activityhub-terraform-state" \
  -backend-config="key=activityhub/terraform.tfstate" \
  -backend-config="region=us-west-2" \
  -backend-config="dynamodb_table=terraform-state-lock"
```

### Environment Management

We use separate variable files for staging and production environments:

#### Staging Environment

```bash
# Create a workspace for staging (if not already created)
terraform workspace new staging

# Switch to staging workspace
terraform workspace select staging

# Plan the deployment for staging
terraform plan -var-file=environments/staging.tfvars

# Apply the changes
terraform apply -var-file=environments/staging.tfvars
```

#### Production Environment

```bash
# Create a workspace for production (if not already created)
terraform workspace new production

# Switch to production workspace
terraform workspace select production

# Plan the deployment for production
terraform plan -var-file=environments/production.tfvars

# Apply the changes
terraform apply -var-file=environments/production.tfvars
```

### Outputs

After applying the Terraform configuration, you'll get various outputs including:

- Cognito User Pool ID and Client ID
- DynamoDB table name
- S3 bucket names
- API Gateway endpoint
- Lambda function details

These outputs can be used in your application configuration.

## Additional Notes

- The Lambda function included is a placeholder. As you develop specific Lambda functions for your application, you'll need to update the Lambda module.
- The S3 bucket notification configuration is commented out and will need to be uncommented and configured once you have created your media processing Lambda function.
- Remember to restrict CORS policies in production to only allow requests from your application domain.
