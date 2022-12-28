variable "project_id" {
  type = string
  default = "task-cf-370908"
}

variable "region" {
  type = string
  default = "us-central1"
}

variable "location" {
  type = string
  default = "US"
}

variable "dataset_id" {
  type = string
  default = "cf_dataset"
}

variable "table_id" {
  type = string
  default = "cf_table"
}

variable "bucket_id" {
  type = string
  default = "task-cf-bucket1"
}

variable "topic_id" {
  type = string
  default = "cf_topic"
}

variable "subscription_id" {
  type = string
  default = "cf_sub"
}