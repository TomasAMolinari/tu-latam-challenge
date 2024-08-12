module "pubsub" {
  source = "./modules/pubsub"

  pubsub_topic_name = var.pubsub_topic_name
}

module "bigquery" {
  source = "./modules/bigquery"

  bigquery_dataset_name = var.bigquery_dataset_name
  bigquery_table_name   = var.bigquery_table_name
}

module "cloudrun" {
  source = "./modules/cloudrun"

  cloud_run_service_name = var.cloud_run_service_name
  project_id             = var.project_id
}