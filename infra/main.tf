terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 5.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "ticket_agent" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_service_plan" "ticket_agent" {
  name                = "${var.app_name}-plan"
  resource_group_name = azurerm_resource_group.ticket_agent.name
  location            = azurerm_resource_group.ticket_agent.location

  os_type  = "Linux"
  sku_name = "B1"
}

resource "azurerm_linux_web_app" "ticket_agent" {
  name                = var.app_name
  resource_group_name = azurerm_resource_group.ticket_agent.name
  location            = azurerm_service_plan.ticket_agent.location
  service_plan_id     = azurerm_service_plan.ticket_agent.id

  site_config {}
}