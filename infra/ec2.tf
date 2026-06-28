# Latest Amazon Linux 2023 AMI (free tier eligible)
data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_security_group" "trading_node" {
  name        = "nixie-trading-node"
  description = "Security group for the Nixie gold trading node"

  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
    description = "SSH"
  }

  # Grafana NodePort — restricted to operator IP
  ingress {
    from_port   = 30300
    to_port     = 30300
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ui_cidr]
    description = "Grafana dashboard"
  }

  # Prometheus NodePort — restricted to operator IP
  ingress {
    from_port   = 30090
    to_port     = 30090
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ui_cidr]
    description = "Prometheus"
  }

  # All outbound (Alpha Vantage API, Telegram, Neon)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "nixie-trading-node"
    Project = "nixie-gold-bot"
  }
}

resource "aws_instance" "trading_node" {
  ami                    = data.aws_ami.al2023.id
  instance_type          = var.instance_type
  key_name               = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.trading_node.id]

  root_block_device {
    volume_type           = "gp2"
    volume_size           = var.root_volume_size_gb
    delete_on_termination = true
    encrypted             = true
  }

  # Enforce IMDSv2 — mitigates SSRF-to-credential-theft
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }

  user_data = templatefile("${path.module}/scripts/user_data.sh", {
    alpha_vantage_key  = var.alpha_vantage_key
    telegram_bot_token = var.telegram_bot_token
    telegram_chat_id   = var.telegram_chat_id
    neon_database_url  = var.neon_database_url
    account_balance    = var.account_balance
  })

  tags = {
    Name    = "nixie-trading-node"
    Project = "nixie-gold-bot"
    Tier    = "free"
  }
}
