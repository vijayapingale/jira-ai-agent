# SQS (Simple Queue Service) configuration for Jira AI Agent

# SQS Queue for ticket processing
resource "aws_sqs_queue" "ticket_processing" {
  name                       = "${local.name_prefix}-ticket-processing"
  visibility_timeout_seconds = 300
  message_retention_seconds  = 1209600  # 14 days
  max_message_size           = 262144    # 256 KB
  delay_seconds              = 0
  receive_wait_time_seconds  = 20

  # Dead Letter Queue
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.ticket_processing_dlq.arn
    maxReceiveCount     = 3
  })

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ticket-processing"
  })
}

# Dead Letter Queue for ticket processing
resource "aws_sqs_queue" "ticket_processing_dlq" {
  name                       = "${local.name_prefix}-ticket-processing-dlq"
  visibility_timeout_seconds = 300
  message_retention_seconds  = 1209600  # 14 days
  max_message_size           = 262144    # 256 KB

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ticket-processing-dlq"
  })
}

# SQS Queue for webhook events
resource "aws_sqs_queue" "webhook_events" {
  name                       = "${local.name_prefix}-webhook-events"
  visibility_timeout_seconds = 60
  message_retention_seconds  = 1209600  # 14 days
  max_message_size           = 262144    # 256 KB
  delay_seconds              = 0
  receive_wait_time_seconds  = 20

  # Dead Letter Queue
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.webhook_events_dlq.arn
    maxReceiveCount     = 5
  })

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-webhook-events"
  })
}

# Dead Letter Queue for webhook events
resource "aws_sqs_queue" "webhook_events_dlq" {
  name                       = "${local.name_prefix}-webhook-events-dlq"
  visibility_timeout_seconds = 60
  message_retention_seconds  = 1209600  # 14 days
  max_message_size           = 262144    # 256 KB

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-webhook-events-dlq"
  })
}

# SQS Queue for background tasks
resource "aws_sqs_queue" "background_tasks" {
  name                       = "${local.name_prefix}-background-tasks"
  visibility_timeout_seconds = 900  # 15 minutes
  message_retention_seconds  = 1209600  # 14 days
  max_message_size           = 262144    # 256 KB
  delay_seconds              = 0
  receive_wait_time_seconds  = 20

  # Dead Letter Queue
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.background_tasks_dlq.arn
    maxReceiveCount     = 2
  })

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-background-tasks"
  })
}

# Dead Letter Queue for background tasks
resource "aws_sqs_queue" "background_tasks_dlq" {
  name                       = "${local.name_prefix}-background-tasks-dlq"
  visibility_timeout_seconds = 900
  message_retention_seconds  = 1209600  # 14 days
  max_message_size           = 262144    # 256 KB

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-background-tasks-dlq"
  })
}

# IAM Role for ECS tasks to access SQS
resource "aws_iam_role_policy" "ecs_sqs_access" {
  name = "${local.name_prefix}-ecs-sqs-access"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "sqs:SendMessage"
        ]
        Resource = [
          aws_sqs_queue.ticket_processing.arn,
          aws_sqs_queue.ticket_processing_dlq.arn,
          aws_sqs_queue.webhook_events.arn,
          aws_sqs_queue.webhook_events_dlq.arn,
          aws_sqs_queue.background_tasks.arn,
          aws_sqs_queue.background_tasks_dlq.arn
        ]
      }
    ]
  })
}

# CloudWatch Alarms for SQS
resource "aws_cloudwatch_metric_alarm" "sqs_ticket_processing_depth" {
  alarm_name          = "${local.name_prefix}-sqs-ticket-processing-depth"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = "300"
  statistic           = "Sum"
  threshold           = "100"

  dimensions = {
    QueueName = aws_sqs_queue.ticket_processing.name
  }

  alarm_actions = [aws_sns_topic.alerts.arn]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-sqs-ticket-depth-alarm"
  })
}

resource "aws_cloudwatch_metric_alarm" "sqs_webhook_events_depth" {
  alarm_name          = "${local.name_prefix}-sqs-webhook-events-depth"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = "300"
  statistic           = "Sum"
  threshold           = "50"

  dimensions = {
    QueueName = aws_sqs_queue.webhook_events.name
  }

  alarm_actions = [aws_sns_topic.alerts.arn]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-sqs-webhook-depth-alarm"
  })
}

resource "aws_cloudwatch_metric_alarm" "sqs_background_tasks_depth" {
  alarm_name          = "${local.name_prefix}-sqs-background-tasks-depth"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = "300"
  statistic           = "Sum"
  threshold           = "25"

  dimensions = {
    QueueName = aws_sqs_queue.background_tasks.name
  }

  alarm_actions = [aws_sns_topic.alerts.arn]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-sqs-background-depth-alarm"
  })
}

# EventBridge Rule for scheduled tasks
resource "aws_cloudwatch_event_rule" "scheduled_tasks" {
  name                = "${local.name_prefix}-scheduled-tasks"
  description         = "Trigger scheduled background tasks"
  schedule_expression = "rate(5 minutes)"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-scheduled-tasks"
  })
}

resource "aws_cloudwatch_event_target" "scheduled_tasks" {
  rule      = aws_cloudwatch_event_rule.scheduled_tasks.name
  target_id = "SendToSQS"
  arn       = aws_sqs_queue.background_tasks.arn

  input_transformer {
    input_paths = {
      time = "$.time"
    }
    input_template = "{\"task_type\": \"scheduled_cleanup\", \"timestamp\": <time>}"
  }
}

# IAM Role for EventBridge to access SQS
resource "aws_iam_role" "events_sqs_role" {
  name = "${local.name_prefix}-events-sqs-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-events-sqs-role"
  })
}

resource "aws_iam_role_policy" "events_sqs_policy" {
  name = "${local.name_prefix}-events-sqs-policy"
  role = aws_iam_role.events_sqs_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sqs:SendMessage"
        Resource = aws_sqs_queue.background_tasks.arn
      }
    ]
  })
}

# Outputs
output "ticket_processing_queue_url" {
  description = "Ticket processing SQS queue URL"
  value       = aws_sqs_queue.ticket_processing.id
}

output "ticket_processing_queue_arn" {
  description = "Ticket processing SQS queue ARN"
  value       = aws_sqs_queue.ticket_processing.arn
}

output "webhook_events_queue_url" {
  description = "Webhook events SQS queue URL"
  value       = aws_sqs_queue.webhook_events.id
}

output "webhook_events_queue_arn" {
  description = "Webhook events SQS queue ARN"
  value       = aws_sqs_queue.webhook_events.arn
}

output "background_tasks_queue_url" {
  description = "Background tasks SQS queue URL"
  value       = aws_sqs_queue.background_tasks.id
}

output "background_tasks_queue_arn" {
  description = "Background tasks SQS queue ARN"
  value       = aws_sqs_queue.background_tasks.arn
}
