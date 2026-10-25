"""Fixture writer for terraform-hcl-function-fold (stdlib only): python3 -I tfh_gen.py <outdir>.
Plans are encoded with stdlib base64 / bytes.hex and split over Terraform locals / variable defaults / heredocs /
join / format / replace / base64decode calls. The expected plain is taken from `terraform console` (see the json)."""
import base64
import json
import sys
from pathlib import Path

out = Path(sys.argv[1])


def plan(cid, uid, fid, adapter, prof):
    return (f"v=3|language=terraform_hcl|role=execution|verdict=malicious|attack=T1059.004|adapter={adapter}|"
            f"host_profile=terraform_hcl_host|obfuscation_profile={prof}|stage_profile=two_stage_download_execute|"
            f"next_language=bash|stage_count=2|steps=acquire_remote,run_stage|campaign_id=TERRAFORM_HCL-{cid}|"
            f"url=https://terraform_hcl-{uid}.example.invalid/stage|file_path=/tmp/huntress-terraform_hcl/.{fid}.stage")


# 1. native HCL, B64, terraform_data host (builtin provider: terraform console needs no init)
b = base64.b64encode(plan("3f9a1c7e", "3f9a1c7e5d", "5d0b8e2a91c4f7e3", "local_exec", "b64").encode()).decode()
q = len(b) // 6
p1, p2, p3, p4, p5 = b[:q], b[q:2 * q], b[2 * q:3 * q], b[3 * q:4 * q], b[4 * q:]
p5t = "~".join(p5[i:i + 7] for i in range(0, len(p5), 7))
(out / "tfh_native_fold.tf").write_text(f'''# HUNTRESS_ANALYSIS_V1:B64-folded
terraform {{
  required_version = ">= 1.3"
}}

variable "seed" {{
  type    = string
  default = "{p1}" # first piece
}}

/* staging locals
   (inert analysis fixture) */
locals {{
  // second piece
  p2 = "{p2}"
  p3 = <<-EOT
    {p3}
    EOT
  p4 = base64decode("{base64.b64encode(p4.encode()).decode()}")
  p5 = replace("{p5t}", "~", "")
  descriptor_3f9a1c7e = format("%s%s%s", "${{var.seed}}${{local.p2}}", trimspace(local.p3), join("", [local.p4, local.p5]))
}}

resource "terraform_data" "stage" {{
  triggers_replace = {{
    run = local.descriptor_3f9a1c7e
  }}
  provisioner "local-exec" {{
    command = "echo ${{local.descriptor_3f9a1c7e}} | base64 -d >/dev/null"
  }}
}}

output "fixture" {{
  value = jsonencode({{ status = "inert-analysis-fixture", n = 1 }})
}}
''')

# 2. JSON grammar (.tf.json), HEX: every string is a template
h = plan("a41d0e6b", "a41d0e6b77", "c2e9f04b6d1a8357", "local_exec", "hex").encode().hex()
t = len(h) // 3
(out / "tfh_json_grammar.tf_json").write_text(json.dumps({
    "variable": {"tail": {"type": "string", "default": h[2 * t:].upper()}},
    "locals": {
        "head": h[:t],
        "mid": "${replace(\"" + "-".join(h[t:2 * t][i:i + 9] for i in range(0, t, 9)) + "\", \"-\", \"\")}",
        "descriptor_a41d0e6b": "${join(\"\", [local.head, local.mid])}${lower(var.tail)}",
    },
    "resource": {"terraform_data": {"stage": {"input": "${local.descriptor_a41d0e6b}"}}},
}, indent=2) + "\n")

# 3. native HCL, B64, null_resource triggers + data "external" program + `<<EOT` heredoc (no indent strip)
b = base64.b64encode(plan("0c6e2f95", "0c6e2f95b1", "8a17d3c0e5f2b946", "external_program", "b64").encode()).decode()
q = len(b) // 3
(out / "tfh_null_external.tf").write_text(f'''# HUNTRESS_ANALYSIS_V1:B64-folded
variable "region" {{
  default = "us-east-1"
}}
locals {{
  a = "{b[:q]}"
  b = <<EOT
{b[q:2 * q]}
EOT
  descriptor_0c6e2f95 = "${{local.a}}${{chomp(local.b)}}${{format("%s", "{b[2 * q:]}")}}"
}}

resource "null_resource" "bootstrap" {{
  triggers = {{
    descriptor_0c6e2f95 = local.descriptor_0c6e2f95
    region              = var.region
  }}
  provisioner "local-exec" {{
    command = "printf %s '${{self.triggers.descriptor_0c6e2f95}}' | base64 -d"
  }}
}}

data "external" "probe" {{
  program = ["sh", "-c", "echo '{{\\"ok\\":\\"1\\"}}'"]
  query   = {{ blob = jsonencode({{ d = local.descriptor_0c6e2f95 }}) }}
}}
''')

# 4. DECOY: same folds, the descriptor is a benign config string (no plan)
d = base64.b64encode(b"region=us-east-1|tier=dev|owner=platform-team|note=inert benign module").decode()
(out / "tfh_decoy_benign.tf").write_text(f'''# benign module
locals {{
  x = "{d[:20]}"
  descriptor_77aa0011 = join("", [local.x, "{d[20:]}"])
}}
resource "terraform_data" "noop" {{
  input = local.descriptor_77aa0011
}}
''')
