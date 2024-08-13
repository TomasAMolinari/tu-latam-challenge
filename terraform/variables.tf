variable "pubsub_topic_name" {
  type        = string
}

variable "bigquery_dataset_name" {
  type        = string
}

variable "bigquery_table_name" {
  type        = string
}

variable "cloud_run_service_name" {
  type        = string
}

variable "project_id" {
  type        = string
  default     = "tu-latam-challenge"
}

variable "region" {
  description = "Región donde se desplegarán los recursos"
  type        = string
  default     = "us-central1"
}