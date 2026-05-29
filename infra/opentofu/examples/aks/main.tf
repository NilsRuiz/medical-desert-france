terraform {
  required_version = ">= 1.6.0"
}

provider "azurerm" {
  features {}
}

module "aks" {
  source = "../../modules/aks"

  name                = var.cluster_name
  resource_group_name = var.resource_group_name
  location            = var.location

  tags = {
    project     = "medical-desert-france"
    environment = var.environment
  }
}

