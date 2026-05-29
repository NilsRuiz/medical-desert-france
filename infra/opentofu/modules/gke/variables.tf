variable "project_id" {
  description = "GCP project id."
  type        = string
}

variable "name" {
  description = "GKE cluster name."
  type        = string
}

variable "location" {
  description = "GCP region or zone for the cluster."
  type        = string
}

variable "network" {
  description = "Existing VPC network self-link or name. TODO: wire a network module for greenfield environments."
  type        = string
}

variable "subnetwork" {
  description = "Existing subnetwork self-link or name."
  type        = string
}

variable "machine_type" {
  description = "Default node pool machine type."
  type        = string
  default     = "e2-standard-4"
}

variable "node_count" {
  description = "Initial node count."
  type        = number
  default     = 2
}

variable "labels" {
  description = "Labels applied to created GCP resources."
  type        = map(string)
  default     = {}
}

