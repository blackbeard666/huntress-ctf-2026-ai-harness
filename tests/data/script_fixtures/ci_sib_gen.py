"""Writes the ci_sib_* fixtures (stdlib only): a v=3 plan, base64-encoded, bound to a bare UPPERCASE
`HUNTRESS_DESCRIPTOR` key (D21 GitHub Actions shape) in the CI siblings: GitLab CI, Azure Pipelines (list + map
variables), CircleCI, Bitbucket, Drone, Buildkite, Tekton. Run: python3 -I ci_sib_gen.py <outdir>"""
import base64, gzip, sys, pathlib
out = pathlib.Path(sys.argv[1])
def plan(lang, cid):
    return (f"v=3|language={lang}|role=downloader|verdict=malicious|attack=T1105|adapter=ci_runner|host_profile=standalone|"
            f"obfuscation_profile=base64|stage_profile=two_stage_download_execute|next_language=powershell|stage_count=2|"
            f"steps=acquire_remote,write_file|campaign_id={lang.upper()}-{cid}|url=https://{lang}-{cid}.example.invalid/stage|"
            f"file_path=/tmp/huntress-{lang}/.{cid}.stage").encode()
b = lambda s: base64.b64encode(s).decode()
F = {}
F["ci_sib_gitlab_top.yml"] = f'''include:
  - project: 'ops/templates'
    file: '/ci/base.yml'
variables:
  GIT_DEPTH: "1"
  HUNTRESS_DESCRIPTOR: "{b(plan('gitlab_ci','4c1d9e02'))}"
.base:
  image: alpine:3.19
  before_script:
    - !reference [.setup, script]
analyze:
  extends: .base
  stage: test
  script:
    - ':'
'''
F["ci_sib_gitlab_job.yml"] = f'''stages: [test]
analyze:
  stage: test
  variables:
    HUNTRESS_DESCRIPTOR_STAGE: "{b(plan('gitlab_ci','77ab0c13'))}"
  script:
    - echo "$HUNTRESS_DESCRIPTOR_STAGE" | base64 -d > /dev/null
'''
F["ci_sib_azure_list.yml"] = f'''trigger: none
pool:
  vmImage: ubuntu-22.04
variables:
- name: buildConfiguration
  value: Release
- name: HUNTRESS_DESCRIPTOR
  value: '{b(plan('azure_pipelines','a90e2f44'))}'
steps:
- task: PowerShell@2
  inputs:
    targetType: inline
    script: |
      Write-Host ':'
'''
F["ci_sib_azure_map.yml"] = f'''trigger:
- main
variables:
  HUNTRESS_DESCRIPTOR: {b(plan('azure_pipelines','0d5b6e71'))}
jobs:
- job: analyze
  steps:
  - pwsh: Write-Host "$(HUNTRESS_DESCRIPTOR)"
'''
F["ci_sib_circleci.yml"] = f'''version: 2.1
orbs:
  node: circleci/node@5.1.0
jobs:
  analyze:
    docker:
      - image: cimg/base:stable
    environment:
      HUNTRESS_DESCRIPTOR: "{b(plan('circleci','5e2c8a10'))}"
    steps:
      - checkout
      - run:
          name: Preserve modeled descriptor
          command: |
            echo ':'
workflows:
  main:
    jobs: [analyze]
'''
F["ci_sib_bitbucket.yml"] = f'''image: atlassian/default-image:4
pipelines:
  default:
    - step:
        name: analyze
        script:
          - export HUNTRESS_DESCRIPTOR="{b(plan('bitbucket_pipelines','3f7d1b09'))}"
          - ':'
'''
F["ci_sib_drone.yml"] = f'''kind: pipeline
type: docker
name: default
steps:
- name: analyze
  image: alpine:3.19
  environment:
    HUNTRESS_DESCRIPTOR: "{b(plan('drone_ci','b2e4c6a8'))}"
  commands:
  - ':'
'''
F["ci_sib_buildkite.yml"] = f'''env:
  HUNTRESS_DESCRIPTOR: "{b(plan('buildkite','91c3d5e7'))}"
steps:
  - label: ":pipeline: analyze"
    command: "echo ok"
'''
F["ci_sib_tekton.yml"] = f'''apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: analyze
spec:
  steps:
    - name: analyze
      image: alpine:3.19
      env:
        - name: HUNTRESS_DESCRIPTOR
          value: "{b(plan('tekton','6a8c0e24'))}"
      script: |
        #!/bin/sh
        echo ':'
'''
F["ci_sib_gitlab_folded.yml"] = '''analyze:
  variables:
    HUNTRESS_DESCRIPTOR: >-
''' + "\n".join("      " + s[i:i+60] for s in [b(plan('gitlab_ci','c0ffee11'))] for i in range(0, len(s), 60)) + '''
  script:
    - ':'
'''
F["ci_sib_gitlab_marker.yml"] = "# HUNTRESS_ANALYSIS_V1:B64-" + b(plan('gitlab_ci', 'e41a7c35')) + f'''
stages: [test]
analyze:
  stage: test
  variables:
    HUNTRESS_DESCRIPTOR: "{b(plan('gitlab_ci','e41a7c35'))}"
  script:
    - ':'
'''
F["ci_sib_decoy_azure_trunc.yml"] = f'''variables:
- name: HUNTRESS_DESCRIPTOR
  value: '{b(plan('azure_pipelines','9d13e5a7'))[:57]}'
steps:
- bash: echo ok
'''
F["ci_sib_decoy_gitlab.yml"] = '''variables:
  HUNTRESS_DESCRIPTOR: "bm90IGEgcGxhbiwganVzdCBhIGJ1aWxkIGNhY2hlIHNlZWQ="
build:
  script:
    - make
'''
for k, v in F.items():
    (out / k).write_text(v)
