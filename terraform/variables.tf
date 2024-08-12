variable "pubsub_topic_name" {
  description = "Nombre del tópico de Pub/Sub"
  type        = string
}

variable "bigquery_dataset_name" {
  description = "Nombre del dataset de BigQuery"
  type        = string
}

variable "bigquery_table_name" {
  description = "Nombre de la tabla de BigQuery"
  type        = string
}

variable "cloud_run_service_name" {
  description = "Nombre del servicio en Cloud Run"
  type        = string
}

variable "project_id" {
  description = "ID del proyecto de GCP"
  type        = string
  default     = "tu-latam-challenge"
}

variable "region" {
  description = "Región donde se desplegarán los recursos"
  type        = string
  default     = "us-central1"
}