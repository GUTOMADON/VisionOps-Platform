module "network" {
  source = "./modules/network"

  project_name        = var.project_name
  environment         = var.environment
  vpc_cidr            = var.vpc_cidr
  public_subnet_cidrs = var.public_subnet_cidrs
  availability_zones  = var.availability_zones
}

module "rds" {
  source = "./modules/rds"

  project_name      = var.project_name
  environment       = var.environment
  subnet_ids        = module.network.public_subnet_ids
  security_group_id = module.network.rds_security_group_id
  db_name           = var.db_name
  db_username       = var.db_username
  db_password       = var.db_password
  db_instance_class = var.db_instance_class
}

module "media_bucket" {
  source = "./modules/s3"

  project_name  = var.project_name
  environment   = var.environment
  force_destroy = var.media_bucket_force_destroy
}

module "ecs" {
  source = "./modules/ecs"

  project_name          = var.project_name
  environment           = var.environment
  aws_region            = var.aws_region
  vpc_id                = module.network.vpc_id
  public_subnet_ids     = module.network.public_subnet_ids
  alb_security_group_id = module.network.alb_security_group_id
  ecs_security_group_id = module.network.ecs_security_group_id
  backend_image         = var.backend_image
  frontend_image        = var.frontend_image
  backend_cpu           = var.backend_cpu
  backend_memory        = var.backend_memory
  frontend_cpu          = var.frontend_cpu
  frontend_memory       = var.frontend_memory
  database_url          = "postgresql+psycopg2://${var.db_username}:${var.db_password}@${module.rds.address}:5432/${var.db_name}"
}
