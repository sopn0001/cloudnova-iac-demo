variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "canadacentral"
}

variable "environment" {
  description = "Environment name (dev, test, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "environment must be dev, test, or prod."
  }
}

variable "app_name" {
  description = "Application workload name"
  type        = string

  validation {
    condition     = length(var.app_name) >= 3 && length(var.app_name) <= 20
    error_message = "app_name must be between 3 and 20 characters."
  }
}

variable "resource_group_name" {
  description = "Existing resource group name"
  type        = string
}

variable "key_vault_id" {
  description = "Key Vault resource ID for application secrets"
  type        = string
}

variable "sql_admin_password_secret_name" {
  description = "Key Vault secret name for SQL password"
  type        = string
  default     = "sql-admin-password"
}

variable "ssh_public_key" {
  description = "SSH public key for the API worker VM"
  type        = string
}

variable "tags" {
  description = "Additional governance tags"
  type        = map(string)
  default     = {}
}

data "azurerm_resource_group" "main" {
  name = var.resource_group_name
}

locals {
  naming_prefix         = "cn-${var.app_name}-${var.environment}"
  storage_account_name  = lower(replace("${local.naming_prefix}st${substr(md5(data.azurerm_resource_group.main.id), 0, 6)}", "-", ""))
  vnet_name             = "${local.naming_prefix}-vnet"
  nsg_name              = "${local.naming_prefix}-nsg"
  nic_name              = "${local.naming_prefix}-nic"
  vm_name               = "${local.naming_prefix}-vm"
  app_service_plan_name = "${local.naming_prefix}-asp"
  web_app_name          = "${local.naming_prefix}-web"

  default_tags = {
    Environment = var.environment
    Application = var.app_name
    Company     = "CloudNova"
    ManagedBy   = "Terraform"
    CostCenter  = "engineering"
    Owner       = "devops-team"
  }

  tags = merge(local.default_tags, var.tags)
}
