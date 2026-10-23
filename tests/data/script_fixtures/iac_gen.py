"""Generator for the iac_* fixtures (cloud-iac-userdata-route): D21-style `v=3|..` plans, XOR 0x41 + hex (the D21
bash `Codec_x='xor_hex|41'` form) carried in Terraform / CloudFormation / ARM / Bicep / Ansible script bodies with the
host's own string semantics (HCL `\\n` / `\\"` escapes, Fn::Join piece lists, ARM `concat()` with `''`, Bicep `\\'`,
YAML double-quoted `\\` line continuation). stdlib only. Run: python3 -I iac_gen.py <outdir>"""
import base64
import json
import sys

out = sys.argv[1]


def plan(lang, cid, role="downloader", attack="T1105"):
    return (f"v=3|language={lang}|role={role}|verdict=malicious|attack={attack}|adapter=http_client|"
            f"host_profile={lang}_host|stage_count=2|steps=acquire_remote,write_file|campaign_id=IAC-{cid}|"
            f"url=https://iac-{cid}.example.invalid/stage|file_path=/tmp/huntress-iac/.{cid}.stage")


def mat(p):
    return bytes(b ^ 0x41 for b in p.encode()).hex()


def bash(cid, m):
    return f"readonly Material_{cid}='{m}'\nreadonly Codec_{cid}='xor_hex|41'\n"


GEN = "python3 -I tests/data/script_fixtures/iac_gen.py tests/data/script_fixtures  (stdlib: XOR 0x41 + hex, D21 bash Material_/Codec_ pair)"
fx = {}

# 1 Terraform local-exec, HCL quoted string with \" and \n escapes, interpreter list
cid = "a1f03c7e"; p = plan("terraform_hcl", cid); m = mat(p)
fx["iac_tf_localexec_escaped.tf"] = (p, f'''terraform {{
  required_version = ">= 1.5"
}}

resource "null_resource" "bootstrap" {{
  triggers = {{ always = timestamp() }}

  provisioner "local-exec" {{
    interpreter = ["/bin/bash", "-c"]
    command     = "readonly Material_{cid}=\\"{m}\\"\\nreadonly Codec_{cid}=\\"xor_hex|41\\"\\necho $${{HOME}} >/dev/null"
  }}
}}
''')

# 2 Terraform user_data = join("", [..]) splitting the material across list items
cid = "b72e9d10"; p = plan("terraform_hcl", cid, "persistence", "T1053"); m = mat(p)
k = len(m) // 2
fx["iac_tf_userdata_join.tf"] = (p, f'''variable "region" {{
  default = "us-east-1"
}}

resource "aws_instance" "worker" {{
  ami           = "ami-0abcdef1234567890"
  instance_type = "t3.micro"
  user_data = base64encode(join("", [
    "#!/bin/bash\\n",
    "readonly Material_{cid}='",
    "{m[:k]}",
    "{m[k:]}",
    "'\\n",
    "readonly Codec_{cid}='xor_hex|41'\\n",
    "echo ${{var.region}}\\n",
  ]))
}}
''')

# 3 decoy: Terraform with benign local-exec / user_data, no codec
fx["iac_tf_decoy_benign.tf"] = (None, '''resource "aws_instance" "web" {
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
''')

# 4 CloudFormation YAML: UserData: Fn::Base64: !Join ['', [..]] (short-form tag, block piece list)
cid = "c4d58a21"; p = plan("cloudformation_yaml", cid); m = mat(p)
k = len(m) // 3
fx["iac_cfn_yaml_join.yaml"] = (p, f'''AWSTemplateFormatVersion: "2010-09-09"
Description: inert analysis stack
Resources:
  WorkerInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0abcdef1234567890
      InstanceType: t3.micro
      UserData:
        Fn::Base64: !Join
          - ''
          - - "#!/bin/bash\\n"
            - "readonly Material_{cid}='"
            - "{m[:k]}"
            - '{m[k:2 * k]}'
            - {m[2 * k:]}
            - "'\\n"
            - !Sub "readonly Codec_{cid}='xor_hex|41'\\n# ${{AWS::Region}}\\n"
''')

# 5 CloudFormation JSON: Fn::Base64 + Fn::Join, material split, Ref in the list
cid = "d9e1f6b3"; p = plan("cloudformation_json", cid, "persistence", "T1053"); m = mat(p)
k = len(m) // 2
doc = {"AWSTemplateFormatVersion": "2010-09-09", "Resources": {"LaunchTpl": {"Type": "AWS::EC2::LaunchTemplate",
       "Properties": {"LaunchTemplateData": {"UserData": {"Fn::Base64": {"Fn::Join": ["", [
           "#!/bin/bash\n", "readonly Material_", cid, "='", m[:k], m[k:], "'\n",
           "readonly Codec_", cid, "='xor_hex|41'\n", "echo ", {"Ref": "AWS::StackName"}, "\n"]]}}}}}}}
fx["iac_cfn_json_join.template"] = (p, json.dumps(doc, indent=2) + "\n")

# 6 decoy: CloudFormation UserData Fn::Join of a benign script (no codec field)
fx["iac_cfn_decoy_benign.yaml"] = (None, '''AWSTemplateFormatVersion: "2010-09-09"
Resources:
  Box:
    Type: AWS::EC2::Instance
    Properties:
      UserData:
        Fn::Base64: !Join
          - ''
          - - "#!/bin/bash\\n"
            - "yum install -y httpd\\n"
            - !Sub "echo ${AWS::StackName} > /var/www/html/index.html\\n"
''')

# 7 ARM deploymentScripts, scriptContent = [concat(..)] with '' escapes, kind AzureCLI
cid = "f3b6c9d2"; p = plan("arm_template", cid); m = mat(p)
k = len(m) // 2
arm = {"$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
       "contentVersion": "1.0.0.0", "resources": [{
           "type": "Microsoft.Resources/deploymentScripts", "apiVersion": "2020-10-01", "name": "bootstrap",
           "location": "[resourceGroup().location]", "kind": "AzureCLI",
           "properties": {"azCliVersion": "2.52.0", "retentionInterval": "P1D",
                          "scriptContent": f"[concat('readonly Material_{cid}=''', '{m[:k]}', '{m[k:]}', '''\n', "
                                           f"'readonly Codec_{cid}=''xor_hex|41''\n', 'echo ', parameters('tag'))]"}}]}
fx["iac_arm_concat.jsonc"] = (p, json.dumps(arm, indent=2) + "\n")

# 8 Bicep single-quoted scriptContent with \' and \n escapes
cid = "a8c2e4f6"; p = plan("bicep", cid); m = mat(p)
fx["iac_bicep_escaped.bicep"] = (p, f'''param location string = resourceGroup().location

resource bootstrap 'Microsoft.Resources/deploymentScripts@2020-10-01' = {{
  name: 'bootstrap'
  location: location
  kind: 'AzureCLI'
  properties: {{
    azCliVersion: '2.52.0'
    retentionInterval: 'P1D'
    scriptContent: 'readonly Material_{cid}=\\'{m}\\'\\nreadonly Codec_{cid}=\\'xor_hex|41\\'\\necho ${{location}}\\n'
  }}
}}
''')

# 9 Ansible: ansible.builtin.shell with a YAML double-quoted cmd, `\\` line continuation splitting the material
cid = "b5d7f9a1"; p = plan("ansible_yaml", cid); m = mat(p)
k = len(m) // 2
fx["iac_ansible_shell_dq.yml"] = (p, f'''- name: inert analysis play
  hosts: all
  become: true
  tasks:
    - name: stage
      ansible.builtin.shell:
        cmd: "readonly Material_{cid}='{m[:k]}\\
          {m[k:]}'\\nreadonly Codec_{cid}='xor_hex|41'\\n"
      args:
        executable: /bin/bash
''')

# 10 decoy: Ansible benign shell task
fx["iac_ansible_decoy_benign.yml"] = (None, '''- hosts: web
  become: true
  tasks:
    - name: restart nginx
      ansible.builtin.shell: systemctl restart nginx
      args:
        executable: /bin/bash
''')

for fn, (p, text) in fx.items():
    with open(f"{out}/{fn}", "w", newline="\n") as f:
        f.write(text)
    stem = fn.rsplit(".", 1)[0]
    ora = ".venv/bin/python -I tests/data/script_fixtures/iac_oracle.py tests/data/script_fixtures/" + fn
    with open(f"{out}/{stem}.json", "w") as f:
        json.dump({"decoy": p is None, "expected_plain": p, "host": "iac",
                   "note": "cloud-iac-userdata-route: script body embedded in an IaC template (lib.codec.iac_scripts / _iac_codecs)",
                   "generator_cmd": GEN, "oracle_cmd": ora + "  (python-hcl2 [pip --target tools/pylib-hcl2] / PyYAML with CFN tag constructors / json "
                   "+ ARM concat evaluator / Bicep regex, then stdlib hex + XOR)"}, f, indent=1)
        f.write("\n")
