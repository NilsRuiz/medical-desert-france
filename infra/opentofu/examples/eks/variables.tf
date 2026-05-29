variable "region" {
  description = "AWS region."
  type        = string
  default     = "eu-west-3"
}

variable "environment" {
  description = "Environment name."
  type        = string
  default     = "dev"
}

variable "cluster_name" {
  description = "EKS cluster name."
  type        = string
  default     = "mdf-dev"
}

variable "kubernetes_version" {
  description = "Kubernetes version."
  type        = string
  default     = "1.30"
}

variable "vpc_id" {
  description = "Existing VPC id."
  type        = string
}

variable "subnet_ids" {
  description = "Existing private subnet ids."
  type        = list(string)
}

variable "node_instance_types" {
  description = "Default node instance types."
  type        = list(string)
  default     = ["t3.large"]
}

