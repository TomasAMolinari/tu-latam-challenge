output "pubsub_topic" {
  value       = module.pubsub.topic_name
}

output "bigquery_table" {
  value       = module.bigquery.table_id
}

output "cloud_run_url" {
  value       = module.cloudrun.url
}