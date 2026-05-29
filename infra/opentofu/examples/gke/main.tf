terraform {
  required_version = ">= 1.6.0"
}

provider "google" {
  project = var.project_id
  region  = var.location
}

module "gke" {
  source = "../../modules/gke"

  project_id = var.project_id
  name       = var.cluster_name
  location   = var.location
  network    = var.network
  subnetwork = var.subnetwork

  labels = {
    project     = "medical-desert-france"
    environment = var.environment
  }
}

