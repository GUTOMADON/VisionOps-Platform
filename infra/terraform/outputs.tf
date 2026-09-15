output "load_balancer_url" {
  description = "Public URL of the application, served by the ALB."
  value       = "http://${module.ecs.load_balancer_dns_name}"
}

output "database_endpoint" {
  description = "Endpoint of the RDS Postgres instance."
  value       = module.rds.endpoint
}

output "media_bucket_name" {
  description = "S3 bucket available for storing model artifacts or media backups."
  value       = module.media_bucket.bucket_name
}

output "ecs_cluster_name" {
  value = module.ecs.cluster_name
}
