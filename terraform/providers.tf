terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
  required_version = ">= 1.2.0"

  backend "s3" {
    # These values will be provided at runtime or via environment variables
    bucket = "activityhub-terraform-state-123"
    key    = "terraform.tfstate"
    region = "eu-west-2"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "ActivityHub"
      Environment = terraform.workspace
      ManagedBy   = "Terraform"
    }
  }
}