resource "google_pubsub_topic" "data_ingest" {
  name = var.pubsub_topic_name
}

resource "google_pubsub_topic" "dead_letter_topic" {
  name = "${var.pubsub_topic_name}-deadman"
}

resource "google_pubsub_subscription" "data_subscription" {
  name  = "${var.pubsub_topic_name}-subscription"
  topic = google_pubsub_topic.data_ingest.name

  retry_policy {
    minimum_backoff = "10s"   
    maximum_backoff = "600s"  
  }

  dead_letter_policy {
    dead_letter_topic = "projects/${var.project_id}/topics/${google_pubsub_topic.dead_letter_topic.name}"
    max_delivery_attempts = 5
  }

  ack_deadline_seconds = 20
}

resource "google_pubsub_subscription" "deadman_subscription" {
  name  = "${google_pubsub_topic.dead_letter_topic.name}-subscription"
  topic = google_pubsub_topic.dead_letter_topic.name
}

output "topic_name" {
  value = google_pubsub_topic.data_ingest.name
}