resource "terraform_data" "first" {
  input = "seed"
}

resource "terraform_data" "drop" {
  triggers_replace = [terraform_data.first.id]
  provisioner "local-exec" {
    interpreter = ["/bin/sh", "-c"]
    command     = "printf \"v=3|role=launcher\\n\" > /tmp/inert.txt && echo \"${self.id}\""
  }
}
