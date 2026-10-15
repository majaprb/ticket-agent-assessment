variable "resource_group_name" {
  description = "Name of the Azure resource group"
  type        = string
  default     = "ticket-agent-rg"
}

variable "location" {
  description = "Azure region for the resources"
  type        = string
  default     = "westeurope"
}

variable "app_name" {
  description = "Name used for the ticket agent application resources"
  type        = string
  default     = "ticket-agent"
}