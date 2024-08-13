resource "google_cloud_run_service" "api_service" {
  name     = var.cloud_run_service_name
  location = "us-central1"
  autogenerate_revision_name = true

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/tu-latam-challenge-api:latest"

        resources {
          limits = {
            memory = "528Mi"
            cpu    = "2"
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

# grants public access (unauthenticated) to the Cloud Run service by assigning the roles/run.invoker role to all users.
resource "google_cloud_run_service_iam_binding" "invoker_binding" {
  location    = google_cloud_run_service.api_service.location
  project     = var.project_id
  service     = google_cloud_run_service.api_service.name
  role        = "roles/run.invoker"
  members     = [
    "allUsers",
  ]
}