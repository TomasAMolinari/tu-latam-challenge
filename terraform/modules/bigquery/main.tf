resource "google_bigquery_dataset" "analytics_dataset" {
  dataset_id = var.bigquery_dataset_name
  location   = "US"
}

resource "google_bigquery_table" "analytics_table" {
  dataset_id = google_bigquery_dataset.analytics_dataset.dataset_id
  table_id   = var.bigquery_table_name
  schema     = <<EOF
[
  {
    "name": "id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "data",
    "type": "STRING",
    "mode": "NULLABLE"
  }
]
EOF
}

output "table_id" {
  value = google_bigquery_table.analytics_table.table_id
}