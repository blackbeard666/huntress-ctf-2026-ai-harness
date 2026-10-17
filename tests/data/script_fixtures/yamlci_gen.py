"""Writes the yamlci_* YAML-host fixtures (GitHub Actions / GitLab CI / Ansible / Argo). Encoding with stdlib only
(base64 / gzip / bytes.hex); the expected plans in the .json files come from the PyYAML oracle_cmd, not lib.codec."""
import base64, gzip, pathlib

D = pathlib.Path(__file__).resolve().parent


def plan(lang, cid, host):
    return (f"v=3|language={lang}|role=persistence|verdict=malicious|attack=T1053|adapter=workflow_cron|"
            f"host_profile={host}|stage_count=2|steps=register_schedule,run_stage|campaign_id=YC-{cid}|"
            f"url=https://yc-{cid}.example.invalid/stage|file_path=/tmp/huntress-yc/.{cid}.stage").encode()


def wrap(s, n, ind):
    return "\n".join(" " * ind + s[i:i + n] for i in range(0, len(s), n))


b64 = lambda b: base64.b64encode(b).decode()
gz = lambda b: gzip.compress(b, 9, mtime=0)
F = {}
# GitHub Actions: workflow_dispatch input whose `default:` is a gzip+base64 `|` block (descriptor key -> nested map)
F["yamlci_gha_input_default.yml"] = (
    "name: release\non:\n  workflow_dispatch:\n    inputs:\n      descriptor_5a1c0e77:\n"
    "        description: build cache seed\n        required: false\n        default: |\n"
    + wrap(b64(gz(plan("github_actions_yaml", "5a1c0e77", "workflow_dispatch"))), 60, 10)
    + "\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n"
    "      - run: echo \"${{ inputs.descriptor_5a1c0e77 }}\" | base64 -d | gunzip | sh\n")
# GitLab CI: `!!binary` tagged block scalar under variables
F["yamlci_gitlab_binary.yml"] = (
    "stages: [build, deploy]\nvariables:\n  GIT_DEPTH: \"1\"\n  DESCRIPTOR_9e33b104: !!binary |\n"
    + wrap(b64(plan("gitlab_ci_yaml", "9e33b104", "gitlab_variables")), 64, 4)
    + "\nbuild:\n  stage: build\n  script:\n    - echo \"$DESCRIPTOR_9e33b104\" > /tmp/.c\n")
# Ansible: Jinja `{{ '<b64>' | b64decode }}` var
F["yamlci_ansible_jinja.yml"] = (
    "---\n- hosts: all\n  become: true\n  vars:\n    descriptor_c40f2a19: \"{{ '"
    + b64(plan("ansible_yaml", "c40f2a19", "ansible_vars")) + "' | b64decode }}\"\n"
    "  tasks:\n    - name: stage\n      ansible.builtin.shell: \"echo {{ descriptor_c40f2a19 }} > /tmp/.s\"\n")
# GitLab CI: hex chunks as an anchored block sequence, referenced through an alias
F["yamlci_gitlab_alias_seq.yml"] = (
    ".chunks: &blob\n" + "\n".join("  - " + c for c in
                                   [x.strip() for x in wrap(plan("gitlab_ci_yaml", "71d0be42", "gitlab_anchor").hex(), 48, 0).split("\n")])
    + "\nvariables:\n  descriptor_71d0be42: *blob\ndeploy:\n  script:\n    - ./deploy.sh\n")
# Argo / k8s env list: `- name: DESCRIPTOR_x` + sibling `value:` plain scalar folded over deeper lines
F["yamlci_argo_env_plain.yml"] = (
    "apiVersion: argoproj.io/v1alpha1\nkind: Workflow\nspec:\n  templates:\n    - name: main\n      container:\n"
    "        image: alpine:3\n        env:\n          - name: DESCRIPTOR_0b7e6d93\n            value: "
    + wrap(b64(plan("argo_yaml", "0b7e6d93", "k8s_env")), 56, 14).lstrip()
    + "\n          - name: MODE\n            value: fast\n        command: [sh, -c]\n")
# DECOYS: benign !!binary text in a GHA workflow; truncated gzip in an inputs default block
F["yamlci_decoy_gha_benign.yml"] = (
    "name: lint\non: [push]\nenv:\n  descriptor_aa11bb22: !!binary |\n"
    + wrap(b64(b"retries=3|cache=npm|node=20|verbose=false|timeout_minutes=15|note=nothing to see here"), 60, 4)
    + "\njobs:\n  lint:\n    runs-on: ubuntu-latest\n    steps:\n      - run: npm ci && npm run lint\n")
F["yamlci_decoy_trunc_gzip.yml"] = (
    "on:\n  workflow_dispatch:\n    inputs:\n      descriptor_dd44ee55:\n        default: |\n"
    + wrap(b64(gz(plan("github_actions_yaml", "dd44ee55", "x"))[:40]), 60, 10) + "\njobs: {}\n")
for n, t in F.items():
    (D / n).write_text(t)
