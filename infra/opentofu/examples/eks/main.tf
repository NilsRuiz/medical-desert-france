terraform {
  required_version = ">= 1.6.0"
}

provider "aws" {
  region = var.region
}

module "eks" {
  source = "../../modules/eks"

  cluster_name        = var.cluster_name
  kubernetes_version  = var.kubernetes_version
  vpc_id              = var.vpc_id
  subnet_ids          = var.subnet_ids
  node_instance_types = var.node_instance_types

  tags = {
    project     = "medical-desert-france"
    environment = var.environment
  }
}

