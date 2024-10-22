variable "AWS_REGION" {
  type = string
  default = "eu-west-2"
}

variable "AWS_ACCESS_KEY" {
  type = string
}

variable "AWS_SECRET_ACCESS_KEY" {
  type = string
}

variable "INPUT_BUCKET_NAME" {
  type = string
}

variable "OUTPUT_BUCKET_NAME" {
  type = string
}

variable "FOLDER_NAME" {
  type = string
}

variable "FROM_ADDRESS" {
  type = string
}

variable "TO_ADDRESS" {
  type = string
}

variable "SUBNET_ID" {
  type = string
}

variable "SECURITY_GROUP_ID" {
  type = string
}

variable "ACCOUNT_ID" {
  type = string
}

variable "PIPELINE_ECR_REPO" {
  type = string
}