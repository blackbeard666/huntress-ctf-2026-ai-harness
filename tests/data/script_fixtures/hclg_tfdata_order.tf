# inert analysis fixture: resources declared out of apply order
terraform {
  required_version = ">= 1.4"
}

locals {
  bundle = "${terraform_data.fetch.id}-${var.region}" // carries a resource ref
  note   = "terraform_data.ghost.id is only text"
  /* terraform_data.cleanup.id inside a comment is no edge */
}

variable "region" {
  default = "us-east-1"
}

resource "terraform_data" "launch" {
  triggers_replace = [local.bundle, "literal terraform_data.cleanup.id"]
  depends_on       = [terraform_data.stage]
  provisioner "local-exec" {
    command = <<-EOT
      echo "launch $${HOME} ${self.id}"
      printf '%s' "${terraform_data.stage.id}"
    EOT
  }
  lifecycle { create_before_destroy = true }
}

resource "terraform_data" "stage" {
  count = 2
  input = { src = terraform_data.fetch.output, tag = "v=3" }
}

resource "terraform_data" "cleanup" {
  for_each = toset(["a", "b"])
  input    = each.key
}

resource "terraform_data" "fetch" {
  input = "https://example.invalid/x"   # no deps
}

output "done" {
  value = terraform_data.launch.id
}
