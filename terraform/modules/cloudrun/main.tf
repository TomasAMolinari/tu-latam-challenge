resource "google_cloud_run_service" "api_service" {
  name     = var.cloud_run_service_name
  location = "us-central1"

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/data-api:latest"

        resources {
          limits = {
            memory = "128Mi"
            cpu    = "1"
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}