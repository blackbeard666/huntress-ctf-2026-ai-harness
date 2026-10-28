#!/usr/bin/env bash
# Fixture writer for target make-recipe-inner-scripts: perl (xor), coreutils base64 / gzip, xxd. Run from this dir.
set -euo pipefail
xorhex() { perl -e '$k=shift; $_=join("",<STDIN>); chomp; print unpack("H*", join("", map { chr(ord($_) ^ $k) } split //))' "$1"; }

# 1. Dockerfile RUN <<EOF heredoc: hex material assembled from two ARGs, xor 0x5a (bash inner script)
P1='v=3|language=dockerfile|role=launcher|verdict=suspicious|attack=T1059.004|next_language=bash|campaign_id=DOCK-7a1b2c3d|url=https://dock-7a1b2c3d.example.invalid/run|file_path=/tmp/.dock-7a1b2c3d.stage'
H1=$(printf '%s' "$P1" | xorhex 90); N=$(( ${#H1} / 2 ))
cat > bis_docker_heredoc_args.Dockerfile <<EOF
# syntax=docker/dockerfile:1.7
FROM alpine:3.20
ARG STAGE_HEAD=${H1:0:$N}
ARG STAGE_TAIL=${H1:$N}
LABEL org.opencontainers.image.title="build-cache-warmer"
RUN <<STAGE
#!/bin/sh
Material_7a1b="\${STAGE_HEAD}\${STAGE_TAIL}"
Codec_7a1b='hex|xor|0x5a'
i=0; out=""
while [ \$i -lt \${#Material_7a1b} ]; do i=\$((i+2)); done
STAGE
CMD ["/bin/true"]
EOF

# 2. Makefile .ONESHELL + SHELL := pwsh recipe: `$$` escaped PowerShell, material from make variables, base64 + xor 0x33
P2='v=3|language=makefile|role=launcher|verdict=suspicious|attack=T1059.001|next_language=powershell|campaign_id=MAKE-5e6f7081|url=https://make-5e6f7081.example.invalid/ps|file_path=C:\\ProgramData\\make-5e6f7081.ps1'
B2=$(printf '%s' "$P2" | perl -e '$_=join("",<STDIN>); print join("", map { chr(ord($_) ^ 0x33) } split //)' | base64 -w0); N=$(( ${#B2} / 2 ))
cat > bis_make_oneshell_pwsh.mk <<EOF
SHELL := pwsh
.SHELLFLAGS := -NoProfile -Command
.ONESHELL:
PART_A := ${B2:0:$N}
PART_B := ${B2:$N}

.PHONY: warm
warm:
	@\$\$Material_5e6f = "\$(PART_A)\$(PART_B)"
	\$\$Codec_5e6f = "base64|xor|0x33"
	\$\$b = [Convert]::FromBase64String(\$\$Material_5e6f)
	Write-Host "cache warm"
EOF

# 3. Dockerfile `RUN echo <b64> | base64 -d | sh`: the whole bash inner script base64'd (hex + xor 0x21 inside)
P3='v=3|language=dockerfile|role=dropper|verdict=malicious|attack=T1027|next_language=bash|campaign_id=DOCK-91a2b3c4|url=https://dock-91a2b3c4.example.invalid/pipe|file_path=/var/tmp/.dock-91a2b3c4'
H3=$(printf '%s' "$P3" | xorhex 33)
S3=$(printf "Material_91a2='%s'\nCodec_91a2='hex|xor|0x21'\necho ok\n" "$H3" | base64 -w0)
cat > bis_docker_echo_pipe.Dockerfile <<EOF
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl \\
    && rm -rf /var/lib/apt/lists/*
RUN echo ${S3} | base64 -d | sh
EOF

# 4. Makefile recipe: marker echoed across a \`\\\`-continued recipe line (the shell joins it)
P4='v=3|language=makefile|role=loader|verdict=suspicious|attack=T1059.004|campaign_id=MAKE-c4d5e6f7|url=https://make-c4d5e6f7.example.invalid/cont|file_path=/tmp/.make-c4d5e6f7'
M4="HUNTRESS_ANALYSIS_V1:B64-$(printf '%s' "$P4" | base64 -w0)"
cat > bis_make_cont_marker.mk <<EOF
.PHONY: all
all:
	@echo "# ${M4:0:72}\\
	${M4:72}"
	-@true
EOF

# decoys: same shapes, nothing plan-shaped behind them
cat > bis_decoy_docker_heredoc.Dockerfile <<EOF
FROM alpine:3.20
ARG STAGE_HEAD=$(printf 'cache-warmer build step, nothing to see' | xorhex 90)
RUN <<STAGE
Material_0d0e="\${STAGE_HEAD}\${STAGE_MISSING}"
Codec_0d0e='hex|xor|0x5a'
STAGE
EOF
cat > bis_decoy_make_oneshell.mk <<EOF
SHELL := /bin/bash
.ONESHELL:
PART_A := $(printf 'make: nothing to be done for all' | base64 -w0)
build:
	@Material_0e0f="\$(PART_A)\$(PART_UNDEFINED)"
	Codec_0e0f='base64|identity|'
	echo "\$\${Material_0e0f}" | base64 -d
EOF
