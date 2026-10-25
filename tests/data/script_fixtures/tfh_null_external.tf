# HUNTRESS_ANALYSIS_V1:B64-folded
variable "region" {
  default = "us-east-1"
}
locals {
  a = "dj0zfGxhbmd1YWdlPXRlcnJhZm9ybV9oY2x8cm9sZT1leGVjdXRpb258dmVyZGljdD1tYWxpY2lvdXN8YXR0YWNrPVQxMDU5LjAwNHxhZGFwdGVyPWV4dGVybmFsX3Byb2dyYW18aG9zdF9wcm9maWxlPXRlcnJhZm9ybV9oY2xfaG9zdHxvYmZ1c2"
  b = <<EOT
NhdGlvbl9wcm9maWxlPWI2NHxzdGFnZV9wcm9maWxlPXR3b19zdGFnZV9kb3dubG9hZF9leGVjdXRlfG5leHRfbGFuZ3VhZ2U9YmFzaHxzdGFnZV9jb3VudD0yfHN0ZXBzPWFjcXVpcmVfcmVtb3RlLHJ1bl9zdGFnZXxjYW1wYWlnbl9pZD1URVJS
EOT
  descriptor_0c6e2f95 = "${local.a}${chomp(local.b)}${format("%s", "QUZPUk1fSENMLTBjNmUyZjk1fHVybD1odHRwczovL3RlcnJhZm9ybV9oY2wtMGM2ZTJmOTViMS5leGFtcGxlLmludmFsaWQvc3RhZ2V8ZmlsZV9wYXRoPS90bXAvaHVudHJlc3MtdGVycmFmb3JtX2hjbC8uOGExN2QzYzBlNWYyYjk0Ni5zdGFnZQ==")}"
}

resource "null_resource" "bootstrap" {
  triggers = {
    descriptor_0c6e2f95 = local.descriptor_0c6e2f95
    region              = var.region
  }
  provisioner "local-exec" {
    command = "printf %s '${self.triggers.descriptor_0c6e2f95}' | base64 -d"
  }
}

data "external" "probe" {
  program = ["sh", "-c", "echo '{\"ok\":\"1\"}'"]
  query   = { blob = jsonencode({ d = local.descriptor_0c6e2f95 }) }
}
