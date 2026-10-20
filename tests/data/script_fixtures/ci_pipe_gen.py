"""Writes the ci_* pipeline-step fixtures (stdlib only): a bash plan carrier (base64 of a single-byte-XOR 0x5a plan)
wrapped in Jenkinsfile / GitLab / GitHub Actions / Azure step bodies. Run: python3 -I ci_pipe_gen.py <outdir>"""
import base64
import sys

out = sys.argv[1]
plan = ("v=1|steps=acquire_remote,write_file,dispatch_process|adapter=curl|stage_count=2|campaign_id=campaign-5be2a1c903"
        "|url=https://5be2a1c903.example.invalid/stage.sh|file_path=/tmp/.cache/stage-5be2a1c903")
mat = base64.b64encode(bytes(b ^ 0x5A for b in plan.encode())).decode()
h = len(mat) // 2
F = {}
F["ci_jenkins_gstring_env.groovy"] = """pipeline {
  agent { docker { image 'alpine:3.19' } }
  environment {
    STAGE_MATERIAL = '%s'
    STAGE_CODEC = 'base64|single_byte_xor|5a'
  }
  stages {
    stage('Fetch') {
      steps {
        sh \"\"\"
readonly Material_5be2a1c9='${STAGE_MATERIAL}'
readonly Codec_5be2a1c9='${env.STAGE_CODEC}'
Load_5be2a1c9() { printf '%%s' "\\${Material_5be2a1c9}" | base64 --decode; }
\"\"\"
      }
    }
  }
}
""" % mat
F["ci_jenkins_concat_script.groovy"] = """node('windows-agent') {
  stage('Stage') {
    def out = sh(label: 'decode', script: "#!/usr/bin/env bash\\nreadonly Material_5be2a1c9='%s" +
        "%s'\\nreadonly Codec_5be2a1c9='base64|single_byte_xor|5a'\\n", returnStdout: true)
    echo out
  }
}
""" % (mat[:h], mat[h:])
F["ci_gitlab_folded.yml"] = """stages: [build]
fetch:
  stage: build
  image: alpine:3.19
  tags: [linux]
  script:
    - >
      readonly Material_5be2a1c9='%s'

      readonly Codec_5be2a1c9='base64|single_byte_xor|5a'
    - "printf '%%s' \\"${Material_5be2a1c9}\\" | base64 -d >/dev/null"
""" % mat
F["ci_gha_env_expr.yml"] = """name: build
on: [push]
env:
  STAGE_MATERIAL: %s
jobs:
  fetch:
    runs-on: ubuntu-latest
    env:
      STAGE_CODEC: "base64|single_byte_xor|5a"
    steps:
      - uses: actions/checkout@v4
      - name: Stage
        shell: bash
        run: |
          readonly Material_5be2a1c9='${{ env.STAGE_MATERIAL }}'
          readonly Codec_5be2a1c9='${{ env.STAGE_CODEC }}'
          printf '%%s' "${Material_5be2a1c9}" | base64 --decode > /dev/null
""" % mat
F["ci_azure_variables.yml"] = """trigger: none
pool:
  vmImage: ubuntu-22.04
variables:
  STAGE_MATERIAL: '%s'
steps:
- bash: |
    readonly Material_5be2a1c9='$(STAGE_MATERIAL)'
    readonly Codec_5be2a1c9='base64|single_byte_xor|5a'
  displayName: Stage
""" % mat
F["ci_jenkins_decoy_unbound.groovy"] = """pipeline {
  agent { label 'linux' }
  stages {
    stage('Fetch') {
      steps {
        sh \"\"\"
readonly Material_5be2a1c9='${STAGE_MATERIAL}'
readonly Codec_5be2a1c9='base64|single_byte_xor|5a'
\"\"\"
      }
    }
  }
}
"""
F["ci_gha_decoy_benign.yml"] = """on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    env:
      STAGE_MATERIAL: not-a-plan
    steps:
      - uses: actions/checkout@v4
      - name: Unit tests
        run: |
          readonly Codec_5be2a1c9='base64|single_byte_xor|5a'
          readonly Material_5be2a1c9='${{ env.STAGE_MATERIAL }}'
          make test
"""
for name, text in F.items():
    with open(f"{out}/{name}", "w") as fh:
        fh.write(text)
