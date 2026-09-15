# Infrastructure - AWS Deployment

Terraform configuration to deploy VisionOps Platform to AWS using ECS Fargate for the backend and frontend containers, an Application Load Balancer, RDS for PostgreSQL, and an S3 bucket for media or model artifact storage.

This configuration favors clarity and low cost over production hardening, since its purpose is to demonstrate a working, reviewable cloud deployment for a portfolio project. See [Notes and simplifications](#notes-and-simplifications) below for what a production deployment would change.

## Architecture deployed

```
Internet
   |
   v
Application Load Balancer (public subnets)
   |            \
   v             v
ECS Fargate    ECS Fargate
frontend       backend  ----> RDS Postgres (same VPC)
                          \
                           --> S3 bucket (media / model artifacts)
```

## Prerequisites

- An AWS account and credentials configured locally (`aws configure` or environment variables).
- Terraform >= 1.6.
- Backend and frontend Docker images already built and pushed to a container registry (ECR recommended). See the root [README](../../README.md#deployment) for the exact `docker build` and `docker push` commands.

## Modules

| Module | Resources |
|---|---|
| [modules/network](modules/network) | VPC, public subnets, internet gateway, route table, security groups for the ALB, ECS tasks and RDS. |
| [modules/rds](modules/rds) | PostgreSQL RDS instance and its subnet group. |
| [modules/s3](modules/s3) | Encrypted, private S3 bucket for media or model artifacts. |
| [modules/ecs](modules/ecs) | ECS cluster, task definitions, services, ALB, target groups and listener rules for the backend and frontend containers. |

## Deploying

Run one command at a time.

```
cd infra/terraform
terraform init
```

```
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your ECR image URIs and a database password, then:

```
terraform plan
```

```
terraform apply
```

Terraform prints `load_balancer_url` when it finishes. Open it in a browser to reach the frontend; the backend is reachable at the same host under `/api/v1`.

## Tearing down

```
terraform destroy
```

This removes every resource created above, including the RDS instance and the S3 bucket (`media_bucket_force_destroy` is `true` by default so the bucket can be deleted even if it still contains objects). Set it to `false` in `terraform.tfvars` if you want Terraform to refuse to delete a non-empty bucket.

## Notes and simplifications

- RDS and the ECS tasks are placed in public subnets with security groups restricting access, instead of a private subnet plus NAT gateway, to avoid the hourly cost of a NAT gateway in a demo deployment. For production, move RDS and the tasks to private subnets.
- There is no HTTPS listener or ACM certificate configured. Add an `aws_lb_listener` on port 443 with a validated certificate for a production domain.
- The backend loads its model from the container image; for frequent model updates, mount the S3 bucket through an init container or a sidecar instead of rebuilding the image every time.
- `db_password` is passed as a Terraform variable for simplicity. For production, source it from AWS Secrets Manager instead of `terraform.tfvars`.
