output "url" {
  description = "URL del servicio desplegado en Cloud Run"
  value       = google_cloud_run_service.api_service.status[0].url
}