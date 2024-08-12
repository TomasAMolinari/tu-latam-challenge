provider "google" {
  project = var.project_id
  region  = var.region
  credentials = file("${path.module}/gcp-terraform-creds.json")
}

provider "google" {
  alias  = "central1"
  region = "us-central1"
}