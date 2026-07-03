output "web_app_url" {
  value = "https://${azurerm_linux_web_app.main.default_hostname}"
}

output "storage_account_name" {
  value = azurerm_storage_account.main.name
}

output "vm_private_ip" {
  value = azurerm_network_interface.main.private_ip_address
}

output "web_app_principal_id" {
  value = azurerm_linux_web_app.main.identity[0].principal_id
}
