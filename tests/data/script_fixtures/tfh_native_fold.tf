# HUNTRESS_ANALYSIS_V1:B64-folded
terraform {
  required_version = ">= 1.3"
}

variable "seed" {
  type    = string
  default = "dj0zfGxhbmd1YWdlPXRlcnJhZm9ybV9oY2x8cm9sZT1leGVjdXRpb258dmVyZGljdD1tYWxpY2lvdXN8YXR0YWNrPVQx" # first piece
}

/* staging locals
   (inert analysis fixture) */
locals {
  // second piece
  p2 = "MDU5LjAwNHxhZGFwdGVyPWxvY2FsX2V4ZWN8aG9zdF9wcm9maWxlPXRlcnJhZm9ybV9oY2xfaG9zdHxvYmZ1c2NhdGlv"
  p3 = <<-EOT
    bl9wcm9maWxlPWI2NHxzdGFnZV9wcm9maWxlPXR3b19zdGFnZV9kb3dubG9hZF9leGVjdXRlfG5leHRfbGFuZ3VhZ2U9
    EOT
  p4 = base64decode("WW1GemFIeHpkR0ZuWlY5amIzVnVkRDB5ZkhOMFpYQnpQV0ZqY1hWcGNtVmZjbVZ0YjNSbExISjFibDl6ZEdGblpYeGpZVzF3WVdsbmJsOXBaRDFVUlZKU1FVWlA=")
  p5 = replace("Uk1fSEN~MLTNmOW~ExYzdlf~HVybD1o~dHRwczo~vL3Rlcn~JhZm9yb~V9oY2wt~M2Y5YTF~jN2U1ZC~5leGFtc~GxlLmlu~dmFsaWQ~vc3RhZ2~V8ZmlsZ~V9wYXRo~PS90bXA~vaHVudH~Jlc3Mtd~GVycmFm~b3JtX2h~jbC8uNW~QwYjhlM~mE5MWM0~ZjdlMy5~zdGFnZQ~==", "~", "")
  descriptor_3f9a1c7e = format("%s%s%s", "${var.seed}${local.p2}", trimspace(local.p3), join("", [local.p4, local.p5]))
}

resource "terraform_data" "stage" {
  triggers_replace = {
    run = local.descriptor_3f9a1c7e
  }
  provisioner "local-exec" {
    command = "echo ${local.descriptor_3f9a1c7e} | base64 -d >/dev/null"
  }
}

output "fixture" {
  value = jsonencode({ status = "inert-analysis-fixture", n = 1 })
}
