"""Generator + oracle for the hcl-resource-dependency-timeline fixtures (offline, not in-window).
Writes hclg_*.tf with stdlib text; `expected` comes from INDEPENDENT readers: `terraform graph` (builtin
terraform_data only, no init / no provider download) for order / anomaly, python-hcl2 for local-exec command bodies.
Run:  python3 -I tests/data/script_fixtures/hclg_gen.py  [PYTHONPATH=<dir holding python-hcl2> for the hcl2 oracle]"""
import json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

TIMELINE = '''# inert analysis fixture: resources declared out of apply order
terraform {
  required_version = ">= 1.4"
}

locals {
  bundle = "${terraform_data.fetch.id}-${var.region}" // carries a resource ref
  note   = "terraform_data.ghost.id is only text"
  /* terraform_data.cleanup.id inside a comment is no edge */
}

variable "region" {
  default = "us-east-1"
}

resource "terraform_data" "launch" {
  triggers_replace = [local.bundle, "literal terraform_data.cleanup.id"]
  depends_on       = [terraform_data.stage]
  provisioner "local-exec" {
    command = <<-EOT
      echo "launch $${HOME} ${self.id}"
      printf '%s' "${terraform_data.stage.id}"
    EOT
  }
  lifecycle { create_before_destroy = true }
}

resource "terraform_data" "stage" {
  count = 2
  input = { src = terraform_data.fetch.output, tag = "v=3" }
}

resource "terraform_data" "cleanup" {
  for_each = toset(["a", "b"])
  input    = each.key
}

resource "terraform_data" "fetch" {
  input = "https://example.invalid/x"   # no deps
}

output "done" {
  value = terraform_data.launch.id
}
'''

LOCALEXEC = '''resource "terraform_data" "first" {
  input = "seed"
}

resource "terraform_data" "drop" {
  triggers_replace = [terraform_data.first.id]
  provisioner "local-exec" {
    interpreter = ["/bin/sh", "-c"]
    command     = "printf \\"v=3|role=launcher\\\\n\\" > /tmp/inert.txt && echo \\"${self.id}\\""
  }
}
'''

DECOY = '''# D28 shape: no resource / data / module block, so no dependency timeline (field absent)
terraform {
  required_version = ">= 1.4"
}

locals {
  plan = "resource terraform_data.x depends_on terraform_data.y"
}

output "plan" {
  value = local.plan
}
'''


def tf_graph(text):
    d = tempfile.mkdtemp()
    try:
        with open(os.path.join(d, "main.tf"), "w") as f:
            f.write(text)
        out = subprocess.run(["terraform", "graph"], cwd=d, capture_output=True, text=True, timeout=120).stdout
    finally:
        shutil.rmtree(d)
    nodes = re.findall(r'^\s*"([^"]+)" \[label=', out, re.M)
    edges = re.findall(r'^\s*"([^"]+)" -> "([^"]+)"', out, re.M)
    return nodes, edges


def file_order(text):
    return ["%s.%s" % m for m in re.findall(r'(?m)^resource "([^"]+)" "([^"]+)"', text)]


def oracle_order(text):
    nodes, edges = tf_graph(text)
    fo = [a for a in file_order(text) if a in nodes]
    deps = {a: {d for x, d in edges if x == a} for a in fo}
    done, order = set(), []
    while len(order) < len(fo):
        nxt = next(a for a in fo if a not in done and deps[a] <= done)
        order.append(nxt)
        done.add(nxt)
    return ",".join(order)


def oracle_anomaly(text):
    nodes, edges = tf_graph(text)
    fo = [a for a in file_order(text) if a in nodes]
    pos = {a: k for k, a in enumerate(fo)}

    def closure(a, seen):
        for x, d in edges:
            if x == a and d not in seen:
                seen.add(d)
                closure(d, seen)
        return seen
    return next((a for a in fo if any(pos[d] > pos[a] for d in closure(a, set()))), None)


def oracle_localexec(text, addr):
    import hcl2
    typ, name = addr.split(".")
    res = hcl2.loads(text)["resource"]
    for r in res:
        for t, body in r.items():
            for n, blk in body.items():
                if t.strip('"') == typ and n.strip('"') == name:
                    for p in blk.get("provisioner", []):
                        for k, v in p.items():
                            if k.strip('"') == "local-exec":
                                return json.loads(v["command"])  # hcl2 keeps the quoted HCL literal; JSON reads it
    return None


def write(name, text, transform, key, expected, oracle, decoy=False):
    with open(os.path.join(HERE, name + ".tf"), "w") as f:
        f.write(text)
    fx = {"material": text, "rep": "hcl_graph", "transform": transform, "key": key, "expected": expected,
          "decoy": decoy, "target": "hcl-resource-dependency-timeline",
          "generator_cmd": "python3 -I tests/data/script_fixtures/hclg_gen.py  (stdlib text writer; copy in %s.tf)" % name,
          "oracle_cmd": oracle}
    with open(os.path.join(HERE, name + ".json"), "w") as f:
        json.dump(fx, f, indent=1)
        f.write("\n")
    print(name, repr(expected))


if __name__ == "__main__":
    tg = "terraform graph (in a temp dir holding the .tf; builtin terraform_data, no init) -> Kahn over its edges, "
    write("hclg_tfdata_order", TIMELINE, "order", "", oracle_order(TIMELINE),
          tg + "file order breaking ties: hclg_gen.oracle_order")
    write("hclg_tfdata_anomaly", TIMELINE, "anomaly", "", oracle_anomaly(TIMELINE),
          tg + "first resource (file order) whose transitive dependency is declared later: hclg_gen.oracle_anomaly")
    write("hclg_tfdata_localexec", LOCALEXEC, "local_exec", "terraform_data.drop",
          oracle_localexec(LOCALEXEC, "terraform_data.drop"),
          "python-hcl2 (pip, lark grammar): hcl2.loads(text)['resource'] -> provisioner local-exec command, "
          "json.loads of the quoted literal: hclg_gen.oracle_localexec")
    nodes, _ = tf_graph(DECOY)
    assert not nodes, nodes
    write("hclg_decoy_no_resources", DECOY, "order", "", None,
          "terraform graph on the .tf prints an empty digraph (no resource nodes) -> field absent", decoy=True)
