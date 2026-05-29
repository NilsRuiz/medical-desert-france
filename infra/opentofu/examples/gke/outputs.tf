output "cluster_name" {
  value = module.gke.cluster_name
}

output "endpoint" {
  value     = module.gke.endpoint
  sensitive = true
}

