terraform {
  backend "gcs" {
    bucket  = "af-test-mihai"
    prefix = "cf/task-cf"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "bucket" {
  name     = var.bucket_id
  location = var.location
  force_destroy = true
}

resource "google_bigquery_table" "table" {
  dataset_id = var.dataset_id
  table_id   = var.table_id
  schema     = file("schemas/schema.json")
  deletion_protection = false
}