# benign module
locals {
  x = "cmVnaW9uPXVzLWVhc3Qt"
  descriptor_77aa0011 = join("", [local.x, "MXx0aWVyPWRldnxvd25lcj1wbGF0Zm9ybS10ZWFtfG5vdGU9aW5lcnQgYmVuaWduIG1vZHVsZQ=="])
}
resource "terraform_data" "noop" {
  input = local.descriptor_77aa0011
}
