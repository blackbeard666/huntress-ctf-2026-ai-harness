# variant C: conditional layers, call/foreach, target SHELL handoff
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
