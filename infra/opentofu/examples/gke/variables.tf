variable "project_id" {
  description = "GCP project id."
  type        = string
}

variable "environment" {
  description = "Environment name."
  type        = string
  default     = "dev"
}

variable "cluster_name" {
  description = "GKE cluster name."
  type        = string
  default     = "mdf-dev"
}

variable "location" {
  description = "GCP region or zone."
  type        = string
  default     = "europe-west9"
}

variable "network" {
  description = "Existing VPC network."
  type        = string
}

variable "subnetwork" {
  description = "Existing subnetwork."
  type        = string
}

