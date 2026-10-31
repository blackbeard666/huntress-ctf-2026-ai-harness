# stage build chain, variant B
PREFIX ?= /opt/stage
CHANNEL := stable
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
all: report launch
launch: decode | prep
	pwsh -NoProfile -Command "Write-Host $(MODE) $(word 2,$(TOOLS))"
decode: fetch
	python3 -c "print('$(CHANNEL)')"
fetch: prep
	@echo fetch $(STAGE_DIR) \
	  $(FIRST)
report: fetch
	node -e "console.log('$(NAME) $(CHANNEL)')"
report: CHANNEL := gamma
prep:
	@echo prep
