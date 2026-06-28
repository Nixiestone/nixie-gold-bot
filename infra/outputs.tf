output "ec2_public_ip" {
  description = "Public IP of the trading node"
  value       = aws_instance.trading_node.public_ip
}

output "ec2_public_dns" {
  description = "Public DNS of the trading node"
  value       = aws_instance.trading_node.public_dns
}

output "grafana_url" {
  description = "Grafana dashboard URL"
  value       = "http://${aws_instance.trading_node.public_ip}:30300"
}

output "prometheus_url" {
  description = "Prometheus URL"
  value       = "http://${aws_instance.trading_node.public_ip}:30090"
}

output "ssh_command" {
  description = "SSH command to access the node"
  value       = "ssh -i ~/.ssh/${var.key_pair_name}.pem ec2-user@${aws_instance.trading_node.public_ip}"
}
