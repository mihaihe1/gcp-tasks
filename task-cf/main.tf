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

resource "google_bigquery_dataset" "dataset_cf" {
  dataset_id = var.dataset_cf_id
  location   = var.location
}

resource "google_bigquery_dataset" "dataset_df" {
  dataset_id = var.dataset_df_id
  location   = var.location
}

resource "google_bigquery_table" "table_messages" {
  dataset_id = google_bigquery_dataset.dataset_df.dataset_id
  table_id   = var.table_messages_id
  schema     = file("schemas/df_tables/messages.json")
  deletion_protection = false
}

resource "google_bigquery_table" "table_err" {
  dataset_id = google_bigquery_dataset.dataset_df.dataset_id
  table_id   = var.table_errors_id
  schema     = file("schemas/df_tables/errors.json")
  deletion_protection = false
}

resource "google_bigquery_table" "table_cf" {
  dataset_id = google_bigquery_dataset.dataset_cf.dataset_id
  table_id   = var.table_cf_id
  schema     = file("schemas/bq_table_schema/task-cf-raw.json")
  deletion_protection = false
}

resource "google_bigquery_table" "table_airflow" {
  dataset_id = google_bigquery_dataset.dataset_df.dataset_id
  table_id   = var.table_af_id
  schema     = file("schemas/af_table/schema.json")
  deletion_protection = false
}

resource "google_pubsub_topic" "topic" {
  name = var.topic_id
}

resource "google_pubsub_subscription" "subscription" {
  name  = var.subscription_id
  topic = google_pubsub_topic.topic.name
}

resource "google_storage_bucket" "bucket_airflow" {
  name     = var.bucket_af_id
  location = var.location
  force_destroy = true
}


resource "google_storage_bucket" "bucket_cf" {
  name     = var.bucket_cf_id
  location = var.location
  force_destroy = true
}

resource "google_storage_bucket_object" "archive" {
  name   = "code.zip"
  source = "function/code.zip"
  bucket = google_storage_bucket.bucket_cf.name
}

resource "google_cloudfunctions_function" "function" {
  name         = "task-function"
  description  = "a new function"

  runtime      = "python310"
  trigger_http = true
  entry_point  = "main"

  source_archive_bucket = google_storage_bucket.bucket_cf.name
  source_archive_object = google_storage_bucket_object.archive.name

  environment_variables = {
    PROJECT_ID    = var.project_id
    OUTPUT_TABLE  = "${google_bigquery_dataset.dataset_cf.dataset_id}.${google_bigquery_table.table_cf.table_id}"
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
