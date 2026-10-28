# terraform_hcl fixture: descriptor only, no marker line
locals {
  huntress_descriptor = replace(<<-EOT, "\n", "")
    dj0zfGxhbmd1YWdlPXRlcnJhZm9ybV9oY2x8cm9sZT1kb3dubG9hZGVyfHZlcmRp
    Y3Q9c3VzcGljaW91c3xhdHRhY2s9VDExMDV8YWRhcHRlcj1odHRwX2NsaWVudHxo
    b3N0X3Byb2ZpbGU9c3RhbmRhbG9uZXxvYmZ1c2NhdGlvbl9wcm9maWxlPWJhc2U2
    NHxzdGFnZV9wcm9maWxlPXR3b19zdGFnZV9kb3dubG9hZF9leGVjdXRlfG5leHRf
    bGFuZ3VhZ2U9anNjcmlwdHxzdGFnZV9jb3VudD0yfHN0ZXBzPWFjcXVpcmVfcmVt
    b3RlLGRpc3BhdGNoX3Byb2Nlc3N8Y2FtcGFpZ25faWQ9VEVSUkFGT1JNX0hDTC01
    Y2IxZDRkNHx1cmw9aHR0cHM6Ly90ZXJyYWZvcm1faGNsLTVjYjFkNGQ0YTUuZXhh
    bXBsZS5pbnZhbGlkL3N0YWdlfGZpbGVfcGF0aD0vdG1wL2h1bnRyZXNzLXRlcnJh
    Zm9ybV9oY2wvLjVjYjFkNGQ0YTU1YWRlOTguc3RhZ2U=
  EOT
}

output "plan" {
  value     = local.huntress_descriptor
  sensitive = false
}

resource "terraform_data" "analysis_fd7f8ed0" {}
