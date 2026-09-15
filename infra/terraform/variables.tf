variable "aws_region" {
  description = "AWS region to deploy into."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Short name used as a prefix for every resource."
  type        = string
  default     = "visionops"
}

variable "environment" {
  description = "Deployment environment name (dev, staging, prod)."
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.20.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for the public subnets, one per availability zone."
  type        = list(string)
  default     = ["10.20.1.0/24", "10.20.2.0/24"]
}

variable "availability_zones" {
  description = "Availability zones to spread subnets across."
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "db_name" {
  description = "Name of the application database."
  type        = string
  default     = "visionops"
}

variable "db_username" {
  description = "Master username for the RDS instance."
  type        = string
  default     = "visionops"
}

variable "db_password" {
  description = "Master password for the RDS instance. Provide through terraform.tfvars or TF_VAR_db_password, never commit it."
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "RDS instance class."
  type        = string
  default     = "db.t3.micro"
}

variable "backend_image" {
  description = "Container image URI for the backend service, e.g. <account>.dkr.ecr.<region>.amazonaws.com/visionops-backend:latest."
  type        = string
}

variable "frontend_image" {
  description = "Container image URI for the frontend service."
  type        = string
}

variable "backend_cpu" {
  description = "Fargate CPU units for the backend task."
  type        = number
  default     = 512
}

variable "backend_memory" {
  description = "Fargate memory (MB) for the backend task."
  type        = number
  default     = 1024
}

variable "frontend_cpu" {
  description = "Fargate CPU units for the frontend task."
  type        = number
  default     = 256
}

variable "frontend_memory" {
  description = "Fargate memory (MB) for the frontend task."
  type        = number
  default     = 512
}

variable "media_bucket_force_destroy" {
  description = "Allow Terraform to delete the media bucket even if it is not empty. Only for demo or teardown convenience."
  type        = bool
  default     = true
}
