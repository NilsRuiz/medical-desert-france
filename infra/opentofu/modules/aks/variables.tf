variable "name" {
  description = "AKS cluster name."
  type        = string
}

variable "resource_group_name" {
  description = "Azure resource group name."
  type        = string
}

variable "location" {
  description = "Azure region."
  type        = string
}

variable "kubernetes_version" {
  description = "AKS Kubernetes version. Keep null to let Azure choose the default."
  type        = string
  default     = null
}

variable "node_count" {
  description = "Default node pool node count."
  type        = number
  default     = 2
}

variable "vm_size" {
  description = "Default node pool VM size."
  type        = string
  default     = "Standard_D4s_v5"
}

variable "tags" {
  description = "Tags applied to created Azure resources."
  type        = map(string)
  default     = {}
}

