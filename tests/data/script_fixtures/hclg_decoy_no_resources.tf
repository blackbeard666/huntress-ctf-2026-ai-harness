# D28 shape: no resource / data / module block, so no dependency timeline (field absent)
terraform {
  required_version = ">= 1.4"
}

locals {
  plan = "resource terraform_data.x depends_on terraform_data.y"
}

output "plan" {
  value = local.plan
}
