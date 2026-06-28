variable "aws_region" {
  description = "AWS region — us-east-1 has the most free-tier services"
  type        = string
  default     = "us-east-1"
}

variable "key_pair_name" {
  description = "Name of an existing EC2 key pair for SSH access"
  type        = string
}

variable "alpha_vantage_key" {
  description = "Alpha Vantage API key (free at alphavantage.co)"
  type        = string
  sensitive   = true
}

variable "telegram_bot_token" {
  description = "Telegram bot token from @BotFather"
  type        = string
  sensitive   = true
}

variable "telegram_chat_id" {
  description = "Telegram chat ID from @userinfobot"
  type        = string
  sensitive   = true
}

variable "neon_database_url" {
  description = "Neon PostgreSQL connection string (postgresql://user:pass@host/db?sslmode=require)"
  type        = string
  sensitive   = true
}

variable "account_balance" {
  description = "Trading account balance in USD (for position sizing)"
  type        = string
  default     = "10000"
}

variable "github_user" {
  description = "GitHub username used to pull images from GHCR"
  type        = string
  default     = "nixiestone"
}

variable "github_token" {
  description = <<-EOT
    GitHub token (classic, scope read:packages) used to pull the service images
    from GHCR. Leave empty if you have made the GHCR packages public — anonymous
    pulls work and the imagePullSecret is simply ignored.
  EOT
  type        = string
  default     = ""
  sensitive   = true
}

variable "instance_type" {
  description = "EC2 instance type — t3.micro (burstable, free-tier eligible 750 hrs/mo) handles the stack better than t2.micro"
  type        = string
  default     = "t3.micro"
}

variable "root_volume_size_gb" {
  description = "Root EBS volume size in GB (free tier: up to 30 GB gp2)"
  type        = number
  default     = 30
}

variable "allowed_ssh_cidr" {
  description = "CIDR block allowed to SSH into the instance. Set to YOUR_IP/32 — do NOT use 0.0.0.0/0."
  type        = string

  validation {
    condition     = var.allowed_ssh_cidr != "0.0.0.0/0"
    error_message = "Refusing to open SSH to the world. Set allowed_ssh_cidr to your IP, e.g. 203.0.113.4/32."
  }
}

variable "allowed_ui_cidr" {
  description = "CIDR block allowed to reach Grafana (30300) and Prometheus (30090). Set to YOUR_IP/32."
  type        = string

  validation {
    condition     = var.allowed_ui_cidr != "0.0.0.0/0"
    error_message = "Refusing to expose Grafana/Prometheus to the world. Set allowed_ui_cidr to your IP, e.g. 203.0.113.4/32."
  }
}
