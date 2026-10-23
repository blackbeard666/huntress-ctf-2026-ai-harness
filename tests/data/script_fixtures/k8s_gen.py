"""Writes the k8s_* manifest fixtures (stdlib only): a D21-style bash plan carrier (Material_/Codec_ readonly pair:
base64 of an add-0x10 plan) wrapped in Kubernetes / Helm manifests -- CronJob `command: [sh, -c]` + block `args`,
ConfigMap `data: |` script, Secret `data:` base64, initContainer flow `command`, Helm `{{ "..." | b64dec }}` and
`{{ .Values.x }}` from a values.yaml doc -- plus decoys. Run: python3 -I k8s_gen.py <outdir>"""
import base64
import json
import sys

out = sys.argv[1]
plan = ("v=1|steps=acquire_remote,write_file,dispatch_process|adapter=busybox_wget_output|stage_count=2"
        "|campaign_id=campaign-7c41e0a9d2|url=https://7c41e0a9d2.example.invalid/k.sh"
        "|user_agent=HuntressLab/7c41e0a9d2|file_path=/var/tmp/.kube-7c41e0a9d2")
mat = base64.b64encode(bytes((b + 0x10) & 0xFF for b in plan.encode())).decode()
body = ("readonly Material_7c41e0a9='%s'\nreadonly Codec_7c41e0a9='base64_literal|add_modulo_256|10'\n"
        "Load_7c41e0a9() { printf '%%s' \"${Material_7c41e0a9}\" | base64 --decode; }\n" % mat)


def ind(t, n):
    return "".join(" " * n + ln + "\n" for ln in t.splitlines())


F = {}
F["k8s_cronjob_args_block.yaml"] = """apiVersion: batch/v1
kind: CronJob
metadata:
  name: node-log-rotate
  namespace: kube-system
spec:
  schedule: "*/15 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          hostPID: true
          containers:
          - name: rotate
            image: alpine:3.19
            securityContext:
              privileged: true
            command: ["/bin/sh", "-c"]
            args:
            - |
%s          restartPolicy: OnFailure
""" % ind(body, 14)
F["k8s_configmap_secret_multidoc.yaml"] = """---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: telemetry
---
apiVersion: v1
kind: Secret
metadata:
  name: telemetry-boot
type: Opaque
data:
  boot.sh: %s
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: telemetry-agent
spec:
  selector:
    matchLabels: {app: telemetry}
  template:
    metadata:
      labels: {app: telemetry}
    spec:
      initContainers:
      - name: boot
        image: busybox:1.36
        command: ["/bin/sh", "/boot/boot.sh"]
      containers:
      - name: agent
        image: busybox:1.36
        command:
        - sleep
        - infinity
      volumes:
      - name: host
        hostPath: {path: /}
""" % base64.b64encode(("#!/bin/sh\n" + body).encode()).decode()
F["k8s_configmap_data_block.yaml"] = """apiVersion: v1
kind: ConfigMap
metadata:
  name: maintenance-scripts
data:
  README: "node maintenance helpers"
  cleanup.sh: |
%s---
apiVersion: batch/v1
kind: Job
metadata:
  name: maintenance
spec:
  template:
    spec:
      containers:
      - name: run
        image: alpine:3.19
        command: ["/bin/sh", "/scripts/cleanup.sh"]
        lifecycle:
          postStart:
            exec:
              command: ["/bin/sh", "-c", "echo started"]
      restartPolicy: Never
""" % ind("#!/bin/sh\n" + body, 4)
F["k8s_helm_b64dec_values.yaml"] = """# Source: values.yaml
stage:
  codec: base64_literal|add_modulo_256|10
  material: %s
---
# Source: telemetry/templates/cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: {{ include "telemetry.fullname" . }}
  labels:
    {{- include "telemetry.labels" . | nindent 4 }}
spec:
  schedule: {{ .Values.schedule | default "0 * * * *" | quote }}
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: {{ .Chart.Name }}
            image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
            command: ["/bin/bash", "-c"]
            args:
            - |
              {{- if .Values.stage.enabled }}
              readonly Material_7c41e0a9='{{ .Values.stage.material }}'
              readonly Codec_7c41e0a9='{{ "%s" | b64dec }}'
              {{- end }}
              Load_7c41e0a9() { printf '%%s' "${Material_7c41e0a9}" | base64 --decode; }
          restartPolicy: OnFailure
""" % (mat, base64.b64encode(b"base64_literal|add_modulo_256|10").decode())
# decoys: a benign Deployment (no carrier), and a Secret whose base64 is truncated mid-material (no plan)
F["k8s_decoy_benign_deploy.yaml"] = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 2
  selector:
    matchLabels: {app: web}
  template:
    metadata:
      labels: {app: web}
    spec:
      containers:
      - name: web
        image: nginx:1.27
        command: ["/bin/sh", "-c", "nginx -g 'daemon off;'"]
        ports:
        - containerPort: 80
"""
trunc = base64.b64encode(("#!/bin/sh\n" + body).encode()).decode()[:120]
F["k8s_decoy_secret_trunc.yaml"] = """apiVersion: v1
kind: Secret
metadata:
  name: boot
data:
  boot.sh: %s
""" % trunc
for fn, txt in F.items():
    open(f"{out}/{fn}", "w").write(txt)
print(plan)
