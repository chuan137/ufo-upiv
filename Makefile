
SAMPLES := sampleB sampleC
NUM_FRAMES := 2

BUILD_TIF := contrast hough likelihood
BUILD_TXT := candidate azimu
BUILDS = $(BUILD_TIF) $(BUILD_TXT)

SCRIPT := ./piv-test.py
OUTBASE := ./res
OUTPUT_TIF := $(OUTBASE)/output.tif
SHELL := /bin/bash

FRAME_LIST = $(shell seq 0 $$(($(NUM_FRAMES)-1)))
SAMPLE_DIRS = $(addprefix $(OUTBASE)/, $(SAMPLES))

define mk_config_file
@cp config_$(lastword $(subst /, ,$(@D))).py $@
@sed -ri "s~([^#]out_file\s+=\s+).*~\1'$(OUTPUT_TIF)',~g" $@
@sed -ri "s/([^#]\s+number\s+=\s+).*/\11,/g" $@
@sed -ri "s/(\s+start\s+=\s+)[0-9]+/\1$(number)/g" $@
@sed -ri "s/(graph = ).*/\1'$(graph)'/g" $@
endef

all: $(BUILD_TIF)
.PHONY: all

$(BUILD_TIF): % : $(SAMPLE_DIRS) $(foreach ff,$(FRAME_LIST), $(foreach dd,$(SAMPLE_DIRS), $(dd)/%_$(ff).tif))
$(BUILD_TXT): % : $(SAMPLE_DIRS) $(foreach ff,$(FRAME_LIST), $(foreach dd,$(SAMPLE_DIRS), $(dd)/%_$(ff).txt))

%.tif: %_config.py
	@cp $< config_tmp.py
	@python $(SCRIPT) config_tmp
	@mv $(OUTPUT_TIF) $@
	@rm config_tmp.py*
%.txt: %_config.py
	@echo $@
	@cp $< config_tmp.py
	@python $(SCRIPT) config_tmp
	@rm config_tmp.py*

%_config.py:
	$(eval graph=$(firstword $(subst _, ,$(*F))))
	$(eval number=$(lastword $(subst _, ,$(*F))))
	$(mk_config_file)

$(SAMPLE_DIRS):
	mkdir -p $@

clean: cleansub
	$(eval empty=$(shell ls -A $(OUTBASE)))
	@if [ "$(empty)" == "" ]; then rm -rf $(OUTBASE); fi
cleansub: 
	rm -rf $(SAMPLE_DIRS)
.PHONY: clean
