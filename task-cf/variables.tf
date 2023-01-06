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

variable "dataset_cf_id" {
  type = string
  default = "cf_dataset"
}

variable "dataset_df_id" {
  type = string
  default = "dataflow"
}

variable "table_cf_id" {
  type = string
  default = "cf_table"
}

variable "table_af_id" {
  type = string
  default = "airflow-messages"
}

variable "table_messages_id" {
  type = string
  default = "messages"
}

variable "table_errors_id" {
  type = string
  default = "errors"
}

variable "bucket_cf_id" {
  type = string
  default = "task-cf-bucket1"
}

variable "bucket_af_id" {
  type = string
  default = "task-cf-370908-af-task"
}

variable "topic_id" {
  type = string
  default = "topic"
}

variable "subscription_id" {
  type = string
  default = "sub"
}