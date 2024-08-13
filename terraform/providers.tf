provider "google" {
  project = var.project_id
  region  = var.region
  credentials = file("${path.module}/../shared/config/gcp_cred.json")
}

provider "google" {
  alias  = "central1"
  region = "us-central1"
}