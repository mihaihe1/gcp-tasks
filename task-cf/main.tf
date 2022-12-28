terraform {
  backend "gcs" {
    bucket  = "cf-test-mihai"
    prefix = "cf/task-cf"
  }
}

#locals {
#  deletion_protection = false
#}

provider "google" {

#  credentials = file("tfsvc.json")

  project = var.project_id
  region  = var.region
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.dataset_id
  location   = var.location
}

resource "google_bigquery_table" "table" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = var.table_id
  schema     = file("schemas/bq_table_schema/task-cf-raw.json")
  deletion_protection = false
}

resource "google_pubsub_topic" "topic" {
  name = var.topic_id
}

resource "google_pubsub_subscription" "subscription" {
  name  = var.subscription_id
  topic = google_pubsub_topic.topic.name
}

resource "google_storage_bucket" "bucket" {
  name     = var.bucket_id
  location = var.location
  force_destroy = true
}

resource "google_storage_bucket_object" "archive" {
  name   = "code.zip"
  source = "function/code.zip"
  bucket = google_storage_bucket.bucket.name
}

resource "google_cloudfunctions_function" "function" {
  name         = "task-function"
  description  = "a new function"

  runtime      = "python310"
  trigger_http = true
  entry_point  = "main"

  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.archive.name

  environment_variables = {
    PROJECT_ID    = var.project_id
    OUTPUT_TABLE  = "${google_bigquery_dataset.dataset.dataset_id}.${google_bigquery_table.table.table_id}"
    TOPIC_ID      = var.topic_id
  }
}

resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = var.project_id
  region         = var.region
  cloud_function = google_cloudfunctions_function.function.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}

#module "task_cf_function" {
#  source              = "modules/cloud_function/main.tf"
#  project_id          = var.project_id
#  name                = "task_cf_function"
#  source_directory    = "function"
#  function_type       = "http"
#  available_memory_mb = 256
#  timeout_s           = 540
#  entry_point         = "main"
#  runtime             = "python38"
#  public_function     = true
#
#  environment_variables = {
#    BDE_GCP_PROJECT = var.project_id
#    OUTPUT_TABLE    = "cf_dataset.task-cf-data"
#    FUNCTION_REGION = "europe-west1"
#  }
#}
#
#module "task_cf_dataset" {
#  project_id = var.project_id
#  dataset_id = "cf_dataset"
#  tables = {
#    task-cf-data = {
#      schema                   = file("schemas/task-cf-raw.json")
#      require_partition_filter = true
#      time_partitioning_field  = "timestamp"
#      time_partitioning_type   = "DAY"
#    }
#  }
#}

