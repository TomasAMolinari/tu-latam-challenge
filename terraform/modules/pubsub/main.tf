resource "google_pubsub_topic" "data_ingest" {
  name = var.pubsub_topic_name
}

resource "google_pubsub_subscription" "data_subscription" {
  name  = "${var.pubsub_topic_name}-subscription"
  topic = google_pubsub_topic.data_ingest.name
}

output "topic_name" {
  value = google_pubsub_topic.data_ingest.name
}