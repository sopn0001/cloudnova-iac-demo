variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "canadacentral"
}

variable "environment" {
  description = "Environment name (dev, test, prod)"
  type        = string
  default     = "dev"
}

variable "app_name" {
  description = "Application workload name"
  type        = string
  default     = "saasapi"
}

# ISSUE: Hardcoded secret — should be Key Vault reference only
variable "sql_admin_password" {
  description = "SQL / VM admin password"
  type        = string
  default     = "P@ssw0rd123!"
  sensitive   = true
}

variable "resource_group_name" {
  description = "Name of the resource group Terraform will create"
  type        = string
}

locals {
  # ISSUE: Non-standard naming — CloudNova requires cn-{app}-{env}-{type}
  storage_account_name  = "storage${substr(md5(azurerm_resource_group.main.id), 0, 8)}"
  vnet_name             = "vnet-${var.app_name}"
  nsg_name              = "nsg-${var.app_name}"
  public_ip_name        = "pip-${var.app_name}"
  nic_name              = "nic-${var.app_name}"
  vm_name               = "vm-${var.app_name}"
  app_service_plan_name = "asp-${var.app_name}"
  web_app_name          = "${var.app_name}-${var.environment}"
}
