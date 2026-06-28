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

variable "instance_type" {
  description = "EC2 instance type — t2.micro is free tier eligible"
  type        = string
  default     = "t2.micro"
}

variable "root_volume_size_gb" {
  description = "Root EBS volume size in GB (free tier: up to 30 GB gp2)"
  type        = number
  default     = 30
}

variable "allowed_ssh_cidr" {
  description = "CIDR block allowed to SSH into the instance"
  type        = string
  default     = "0.0.0.0/0"  # Restrict to your IP in production
}
