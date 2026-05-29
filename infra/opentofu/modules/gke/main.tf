resource "google_container_cluster" "this" {
  project  = var.project_id
  name     = var.name
  location = var.location

  network    = var.network
  subnetwork = var.subnetwork

  remove_default_node_pool = true
  initial_node_count       = 1

  release_channel {
    channel = "REGULAR"
  }

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  resource_labels = var.labels
}

resource "google_container_node_pool" "default" {
  project    = var.project_id
  name       = "default"
  location   = var.location
  cluster    = google_container_cluster.this.name
  node_count = var.node_count

  node_config {
    machine_type = var.machine_type
    labels       = var.labels
    oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }
}

# TODO: add private cluster settings, authorized networks, Cloud SQL, Artifact Registry, node autoscaling, and managed certificates.

