SHELL := /bin/bash

-include Makefile.conf

CURRENT_DIR = $(shell pwd)
SAMPLE_DIRS = $(addprefix $(OUTROOT)/, $(SAMPLES))

# find all image files and txt files
IMG_FILES = $(sort $(foreach dd,$(SAMPLES), $(wildcard $(DATAROOT)/$(dd)/*.tif)))
TXT_FILES = $(sort $(foreach dd,$(SAMPLES),$(wildcard $(OUTROOT)/$(dd)/*.txt)))

# build list of output files
OUT_TEMPLATE = $(foreach ff,$(IMG_FILES),$(dir $(ff))%_$(notdir $(ff)))
OUT_TIFS = $(OUT_TEMPLATE:$(DATAROOT)/%=$(OUTROOT)/%)
OUT_TXTS = $(OUT_TEMPLATE:$(DATAROOT)/%.tif=$(OUTROOT)/%.txt)
OUT_PNGS = $(TXT_FILES:%.txt=%.png)

all: $(BUILD_TIF) $(BUILD_TXT)
.PHONY: all plots

$(BUILD_TIF): % : $(SAMPLE_DIRS) $(OUT_TIFS)
$(BUILD_TXT): % : $(SAMPLE_DIRS) $(OUT_TXTS)
plots : $(OUT_PNGS)

print-%: 
	@echo $* = $($*)

%.png:
	@echo $@
	$(eval number=$(lastword $(subst _, ,$(*F))))
	$(eval sample=$(lastword $(subst /, ,$(*D))))
	@../tests/plot-rings.py $(DATAROOT)/$(sample)/$(number).tif $*.txt 2> $(OUTPUT_TMP)

$(SAMPLE_DIRS):
	mkdir -p $@

clean: cleansub
	$(eval empty=$(shell ls -A $(OUTROOT)))
	@if [ "$(empty)" == "" ]; then rm -rf $(OUTROOT); fi
cleansub: 
	rm -rf $(SAMPLE_DIRS)
.PHONY: clean

define mk_config_file
@sed -ri "s~(^out_file\s+:\s+).*~\1'$@'~g" $(CONFIG_TMP)
@sed -ri "s/(^number\s+:\s+).*/\11/g" $(CONFIG_TMP)
@sed -ri "s/(^start\s+:\s+)[0-9]+/\1$(number)/g" $(CONFIG_TMP)
@sed -ri "s/(^graph\s+:\s+).*/\1'$(graph)'/g" $(CONFIG_TMP)
endef

.SECONDEXPANSION:

%.tif %.txt: $$(lastword $$(subst /, ,$$(@D))).cfg
	@echo $@
	$(eval graph=$(firstword $(subst _, ,$(*F))))
	$(eval number=$(shell echo $(lastword $(subst _, ,$(*F))) | sed -r 's/^0*([0-9]+)/\1/' )) 
	$(eval sample=$(lastword $(subst /, ,$(*D))))
	@cp $(sample).cfg $(CONFIG_TMP)
	$(mk_config_file)
	@python $(SCRIPT) $(CONFIG_TMP) 2> $(OUTPUT_TMP)
	@rm $(CONFIG_TMP)
