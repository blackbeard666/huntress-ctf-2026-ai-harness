"""Writes the make-target-flow-variant-diff fixture variants (stdlib only): two Makefiles differing in one `?=`
override (CHANNEL pinned with `:=` ahead of the `?=` in B) and one prereq swap (`all: launch report` -> `all: report
launch`), plus a Dockerfile impostor. Usage: python3 -I mkflow_gen.py <outdir>"""
import sys
from pathlib import Path

A = """# stage build chain, variant A
PREFIX ?= /opt/stage
CHANNEL ?= beta
STAGE_DIR := $(PREFIX)/drop
TOOLS = fetch $(EXTRA)
EXTRA = decode
TOOLS += launch
override MODE := quiet
MODE := loud
NAME = $(strip $(subst -,_, stage-one ))
FIRST = $(firstword $(TOOLS))
OBJS := $(patsubst %.c,%.o,a.c b.c)
define HOOK
import sys
print("hook")
endef
.PHONY: all fetch decode launch report prep
.DEFAULT_GOAL := all
all: launch report
launch: decode | prep
\tpwsh -NoProfile -Command "Write-Host $(MODE) $(word 2,$(TOOLS))"
decode: fetch
\tpython3 -c "print('$(CHANNEL)')"
fetch: prep
\t@echo fetch $(STAGE_DIR) \\
\t  $(FIRST)
report: fetch
\tnode -e "console.log('$(NAME) $(CHANNEL)')"
report: CHANNEL := gamma
prep:
\t@echo prep
"""
B = A.replace("variant A", "variant B").replace("CHANNEL ?= beta", "CHANNEL := stable\nCHANNEL ?= beta") \
     .replace("all: launch report", "all: report launch").replace(".DEFAULT_GOAL := all\n", "")
D = """FROM alpine:3.20
ARG HUNTRESS_DESCRIPTOR_0badf00d=deadbeef
RUN echo build && make all
CMD ["/bin/sh", "-c", "echo run"]
"""
out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
(out / "mkflow_variant_a.mk").write_text(A)
(out / "mkflow_variant_b.mk").write_text(B)
(out / "mkflow_impostor.dockerfile").write_text(D)
C = """# variant C: conditional layers, call/foreach, target SHELL handoff
MODE ?= dev
ifeq ($(MODE),dev)
  PAYLOAD := $(call wrap,dev)
  STEPS = one two
else ifdef CI
  STEPS = ci
else
  STEPS = never
endif
wrap = [$(1)-$(words $(STEPS))]
PAYLOAD2 = $(call wrap,late)
LIST := $(foreach s,$(STEPS),step_$(s))
ifndef UNSET_X
  STEPS += three
endif
.RECIPEPREFIX = >
deploy: $(LIST) ; @echo deploy
step_%:
>@echo $@
stage: SHELL := /usr/bin/python3
stage: .SHELLFLAGS := -c
stage: deploy
>print("$(PAYLOAD2)")
"""
(out / "mkflow_variant_c.mk").write_text(C)
