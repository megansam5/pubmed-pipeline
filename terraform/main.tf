provider "aws" {
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_ACCESS_KEY
}

# ECR with pipeline image
data "aws_ecr_image" "pipeline_image" {
  repository_name = var.PIPELINE_ECR_REPO
  image_tag       = "latest"
}

# IAM role for running ECS task (already a role)
data "aws_iam_role" "execution-role" {
  name = "ecsTaskExecutionRole"
}

# Task definition for ECS task
resource "aws_ecs_task_definition" "pipeline-task-definition" {
  family = "c13-megan-pharma-pipeline-task-def"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  execution_role_arn = data.aws_iam_role.execution-role.arn
  cpu       = 256
  memory    = 512
  container_definitions = jsonencode([
    {
      name      = "c13-megan-pharma-pipeline"
      image     = data.aws_ecr_image.pipeline_image.image_uri
      essential = true
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
        }
      ]
      environment = [
        {
            name="OUTPUT_BUCKET_NAME"
            value=var.OUTPUT_BUCKET_NAME
        },
        {
            name="INPUT_BUCKET_NAME"
            value=var.INPUT_BUCKET_NAME
        },
        {
            name="FOLDER_NAME"
            value=var.FOLDER_NAME
        },
        {
            name="AWS_ACCESS_KEY"
            value=var.AWS_ACCESS_KEY
        },
        {
            name="AWS_SECRET_ACCESS_KEY"
            value=var.AWS_SECRET_ACCESS_KEY
        }
      ]
      logConfiguration = {
                logDriver = "awslogs"
                "options": {
                    awslogs-group = "/ecs/c13-megan-pharma-pipeline-task-def"
                    awslogs-stream-prefix = "ecs"
                    awslogs-region = "eu-west-2"
                    mode = "non-blocking"
                    max-buffer-size = "25m"
                }
      }
    }])
}

# Permissions for the state machine

# Assuming the role for state machine
data  "aws_iam_policy_document" "state-machine-trust-policy" {
    statement {
        effect = "Allow"
        principals {
            type        = "Service"
            identifiers = ["states.amazonaws.com"]
        }
        actions = ["sts:AssumeRole"]
    }
}

# Permissions for role: running ESC task, IAM pass role, events (for syncing), sending email
data  "aws_iam_policy_document" "state-machine-permissions-policy" {
    statement {
        effect = "Allow"
        resources = [
                aws_ecs_task_definition.pipeline-task-definition.arn
            ]
        actions = [
            "ecs:RunTask"
        ]
    }
    statement {
      effect = "Allow"
      actions = [
        "iam:PassRole"
      ]
      resources = [
        "arn:aws:iam::${var.ACCOUNT_ID}:role/ecsTaskExecutionRole"
      ]
    }

    statement {
      effect = "Allow"
      actions = [
        "events:PutTargets",
        "events:PutRule",
        "events:DescribeRule"
      ]
      resources = ["*"]    
      }


    statement {
      effect = "Allow"
      resources = [
        "arn:aws:ses:eu-west-2:${var.ACCOUNT_ID}:identity/${var.FROM_ADDRESS}"
      ]
      actions = [
        "ses:SendEmail"
      ]
    }
}

# IAM role for step function
resource "aws_iam_role" "state-machine-role" {
    name               = "c13-megan-pharma-state-role"
    assume_role_policy = data.aws_iam_policy_document.state-machine-trust-policy.json 
}

# Adding the policies to role
resource "aws_iam_role_policy" "state-machine-role-policy" {
  name   = "c13-megan-pharma-state-policy"
  role   = aws_iam_role.state-machine-role.id
  policy = data.aws_iam_policy_document.state-machine-permissions-policy.json
}


# The cluster to run tasks on
data "aws_ecs_cluster" "c13-cluster" {
    cluster_name = "c13-ecs-cluster"
}

# A public subnet
data "aws_subnet" "c13-public-subnet" {
    id = var.SUBNET_ID
}

# The default security group
data "aws_security_group" "c13-default-sg" {
    id = var.SECURITY_GROUP_ID
}

# The state machine to send email, run task and then send email

resource "aws_sfn_state_machine" "sfn_state_machine" {
  name     = "c13-megan-pharma-state-machine"
  role_arn = aws_iam_role.state-machine-role.arn

  definition = <<EOF
{
  "Comment": "A description of my state machine",
  "StartAt": "SendEmail",
  "States": {
            "SendEmail": {
            "Type": "Task",
            "Parameters": {
        "FromEmailAddress": "${var.FROM_ADDRESS}",
        "Destination": {
            "ToAddresses": [
            "${var.TO_ADDRESS}"
            ]
        },
        "Content": {
            "Simple": {
            "Body": {
                "Text": {
                "Data": "Hello, just an email to let you know a new xml file has been uploaded so processsing has begun."
                }
            },
            "Subject": {
                "Data": "Data Process Started"
            }
            }
        }
        },
      "Resource": "arn:aws:states:::aws-sdk:sesv2:sendEmail",
      "Next": "ECS RunTask"
    },
    "ECS RunTask": {
      "Type": "Task",
      "Resource": "arn:aws:states:::ecs:runTask.sync",
      "Parameters": {
        "LaunchType": "FARGATE",
        "Cluster": "${data.aws_ecs_cluster.c13-cluster.arn}",
        "TaskDefinition": "${aws_ecs_task_definition.pipeline-task-definition.arn}",
        "NetworkConfiguration": {
            "AwsvpcConfiguration": {
            "Subnets": ["${data.aws_subnet.c13-public-subnet.id}"], 
            "SecurityGroups": ["${data.aws_security_group.c13-default-sg.id}"],
            "AssignPublicIp": "ENABLED"
  }
}
      },
      "Next": "SendEmail (1)"
    },
            "SendEmail (1)": {
            "Type": "Task",
            "Parameters": {
        "FromEmailAddress": "${var.FROM_ADDRESS}",
        "Destination": {
            "ToAddresses": [
            "${var.TO_ADDRESS}"
            ]
        },
        "Content": {
            "Simple": {
            "Body": {
                "Text": {
                "Data": "Hello, just an email to let you know the processing is complete and a new csv file has been uploaded to s3."
                }
            },
            "Subject": {
                "Data": "Data Processing Complete"
            }
            }
        }
        },
      "Resource": "arn:aws:states:::aws-sdk:sesv2:sendEmail",
      "End": true
    }
  }
}
EOF
}

# Permissions for the eventbridge

# Assume the role for eventbridge 
data  "aws_iam_policy_document" "eventbridge-trust-policy" {
    statement {
        effect = "Allow"
        principals {
            type        = "Service"
            identifiers = ["events.amazonaws.com"]
        }
        actions = ["sts:AssumeRole"]
    }
}

# Permissions for role: starting step function state machine
data  "aws_iam_policy_document" "eventbridge-permissions-policy" {
    statement {
        effect = "Allow"
        resources = [
                aws_sfn_state_machine.sfn_state_machine.arn
            ]
        actions = [
            "states:StartExecution"
        ]
    }
}

# IAM role for eventbridge
resource "aws_iam_role" "eventbridge-role" {
    name               = "c13-megan-eventbridge-pubmed-role"
    assume_role_policy = data.aws_iam_policy_document.eventbridge-trust-policy.json
}

# Adding the policies to role
resource "aws_iam_role_policy" "eventbridge-role-policy" {
  name   = "c13-megan-eventbridge-state-policy"
  role   = aws_iam_role.eventbridge-role.id
  policy = data.aws_iam_policy_document.eventbridge-permissions-policy.json
}


# Event rule - file put into s3 bucket

resource "aws_cloudwatch_event_rule" "event_rule" {
  name        = "c13-megan-add-pubmed-file-rule"
  

  event_pattern = jsonencode({
    "source": ["aws.s3"],
  "detail-type": ["Object Created"],
  "detail": {
    "bucket": {
      "name": [var.INPUT_BUCKET_NAME]
    },
    "object": {
      "key": [{
        "wildcard": "${var.FOLDER_NAME}/*.xml"
      }]
    }
  }
  })
}

# Event target - running step function

resource "aws_cloudwatch_event_target" "step_function_target" {
  rule      = aws_cloudwatch_event_rule.event_rule.name
  target_id = "StepFunction"
  arn       = aws_sfn_state_machine.sfn_state_machine.arn
  role_arn = aws_iam_role.eventbridge-role.arn
}