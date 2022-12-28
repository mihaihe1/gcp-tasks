resource "google_cloudfunctions_function" "function"{
  project_id          = "var.project_id"
  name                = "task_cf_function"
  source_directory    = "function"
  function_type       = "http"
  available_memory_mb = 256
  timeout_s           = 540
  entry_point         = "main"
  runtime             = "python38"
  public_function     = true

  environment_variables = {
    BDE_GCP_PROJECT = var.project_id
    OUTPUT_TABLE    = "cf_dataset.task-cf-data"
    FUNCTION_REGION = "europe-west1"
  }
}