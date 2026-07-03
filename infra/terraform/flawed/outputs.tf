output "web_app_url" {
  value = "https://${azurerm_linux_web_app.main.default_hostname}"
}

output "storage_account_name" {
  value = azurerm_storage_account.main.name
}

output "vm_public_ip" {
  description = "Public IP of the API worker VM"
  value       = azurerm_public_ip.main.ip_address
}

output "orphan_disk_id" {
  description = "Unattached disk still incurring cost"
  value       = azurerm_managed_disk.orphan_backup.id
}
