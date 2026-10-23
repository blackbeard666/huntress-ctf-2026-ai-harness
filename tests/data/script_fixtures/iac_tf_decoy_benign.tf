resource "aws_instance" "web" {
  ami       = "ami-0abcdef1234567890"
  user_data = base64encode(<<-EOT
    #!/bin/bash
    yum install -y nginx
    systemctl enable --now nginx
  EOT
  )
  provisioner "local-exec" {
    command = "echo ${self.private_ip} >> hosts.txt"
  }
}
