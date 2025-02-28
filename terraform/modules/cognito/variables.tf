variable "app_name" {
  description = "Application name"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "auto_verify" {
  description = "Auto verify email"
  type        = bool
  default     = true
}
