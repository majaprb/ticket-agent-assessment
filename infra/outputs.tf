output "resource_group_name" {
  description = "Name of the Azure resource group"
  value       = azurerm_resource_group.ticket_agent.name
}

output "web_app_name" {
  description = "Name of the Linux Web App"
  value       = azurerm_linux_web_app.ticket_agent.name
}

output "web_app_hostname" {
  description = "Default hostname of the Linux Web App"
  value       = azurerm_linux_web_app.ticket_agent.default_hostname
}