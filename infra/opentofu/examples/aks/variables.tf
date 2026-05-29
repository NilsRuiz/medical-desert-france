variable "environment" {
  description = "Environment name."
  type        = string
  default     = "dev"
}

variable "cluster_name" {
  description = "AKS cluster name."
  type        = string
  default     = "mdf-dev"
}

variable "resource_group_name" {
  description = "Existing Azure resource group."
  type        = string
}

variable "location" {
  description = "Azure region."
  type        = string
  default     = "francecentral"
}

