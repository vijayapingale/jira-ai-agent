# RDS (Relational Database Service) configuration for PostgreSQL with pgvector

# Subnet Group for RDS
resource "aws_db_subnet_group" "main" {
  name       = "${local.name_prefix}-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-subnet-group"
  })
}

# Security Group for RDS
resource "aws_security_group" "rds" {
  name        = "${local.name_prefix}-rds-sg"
  description = "Security group for RDS database"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-rds-sg"
  })
}

# Random password for RDS
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Store DB password in Secrets Manager
resource "aws_secretsmanager_secret" "db_credentials" {
  name = "${local.name_prefix}-db-credentials"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-credentials"
  })
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = "jira_ai_agent"
    password = random_password.db_password.result
    dbname   = "jira_ai_agent"
    host     = aws_db_instance.main.address
    port     = aws_db_instance.main.port
  })
}

# RDS Instance (PostgreSQL with pgvector)
resource "aws_db_instance" "main" {
  identifier = "${local.name_prefix}-db"

  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.medium"

  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_type          = "gp2"
  storage_encrypted     = true

  db_name  = "jira_ai_agent"
  username = "jira_ai_agent"
  password = random_password.db_password.result

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  skip_final_snapshot       = false
  final_snapshot_identifier = "${local.name_prefix}-db-final-snapshot-${timestamp()}"
  delete_automated_backups  = false

  performance_insights_enabled = true
  performance_insights_retention_period = 7

  deletion_protection = false

  # Enable pgvector extension
  parameter_group_name = aws_db_parameter_group.main.name

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db"
  })
}

# Custom Parameter Group for pgvector
resource "aws_db_parameter_group" "main" {
  name   = "${local.name_prefix}-pgvector-params"
  family = "postgres15"

  parameter {
    name  = "shared_preload_libraries"
    value = "pgvector"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-pgvector-params"
  })
}

# Additional Secrets
resource "aws_secretsmanager_secret" "db_url" {
  name = "${local.name_prefix}-db-url"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-url"
  })
}

resource "aws_secretsmanager_secret_version" "db_url" {
  secret_id = aws_secretsmanager_secret.db_url.id
  secret_string = "postgresql://${random_password.db_password.result}@${aws_db_instance.main.address}:${aws_db_instance.main.port}/jira_ai_agent"
}

resource "aws_secretsmanager_secret" "openai_key" {
  name = "${local.name_prefix}-openai-key"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-openai-key"
  })
}

resource "aws_secretsmanager_secret" "jira_token" {
  name = "${local.name_prefix}-jira-token"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-jira-token"
  })
}

resource "aws_secretsmanager_secret" "confluence_token" {
  name = "${local.name_prefix}-confluence-token"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-confluence-token"
  })
}

# CloudWatch Alarms for RDS
resource "aws_cloudwatch_metric_alarm" "db_cpu" {
  alarm_name          = "${local.name_prefix}-db-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  alarm_actions = [aws_sns_topic.alerts.arn]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-cpu-alarm"
  })
}

resource "aws_cloudwatch_metric_alarm" "db_memory" {
  alarm_name          = "${local.name_prefix}-db-memory-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "FreeableMemory"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "268435456"  # 256 MB

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  alarm_actions = [aws_sns_topic.alerts.arn]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-memory-alarm"
  })
}

resource "aws_cloudwatch_metric_alarm" "db_storage" {
  alarm_name          = "${local.name_prefix}-db-storage-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = "600"
  statistic           = "Average"
  threshold           = "10737418240"  # 10 GB

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  alarm_actions = [aws_sns_topic.alerts.arn]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-storage-alarm"
  })
}

# SNS Topic for alerts
resource "aws_sns_topic" "alerts" {
  name = "${local.name_prefix}-alerts"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-alerts"
  })
}

# Outputs
output "db_instance_id" {
  description = "RDS instance ID"
  value       = aws_db_instance.main.id
}

output "db_instance_address" {
  description = "RDS instance address"
  value       = aws_db_instance.main.address
}

output "db_instance_port" {
  description = "RDS instance port"
  value       = aws_db_instance.main.port
}

output "db_credentials_secret_arn" {
  description = "ARN of the database credentials secret"
  value       = aws_secretsmanager_secret.db_credentials.arn
}
