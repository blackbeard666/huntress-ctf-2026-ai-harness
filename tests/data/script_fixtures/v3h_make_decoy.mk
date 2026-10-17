# build helpers
DESCRIPTOR_BD9FAFBE := YnVpbGQgY2FjaGUgd2FybXVwIGZvciB0aGUgbmlnaHRseSBpbnZlbnRvcnk7IG5v\
dGhpbmcgdG8gZXhlY3V0ZQ==

all:
	@echo $(words $(DESCRIPTOR_BD9FAFBE))

.PHONY: all
