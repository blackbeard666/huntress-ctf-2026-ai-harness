# HUNTRESS_ANALYSIS_V1:B64-c3RhdHVzPW9rO2luZXJ0LWFuYWx5c2lzLWZpeHR1cmU7bm8gcGxhbiBoZXJl
locals {
  huntress_descriptor = trimspace(<<-EOT
    c3RhdHVzPW9rO2luZXJ0LWFuYWx5c2lzLWZpeHR1cmU7bm8gcGxhbiBoZXJl
  EOT
  )
}

output "plan" {
  value     = local.huntress_descriptor
  sensitive = false
}

resource "terraform_data" "analysis_2b8d7583" {}
