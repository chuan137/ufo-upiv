
SAMPLES := sampleB sampleC
NUM_FRAMES := 10

BUILD_TIF := contrast hough likelihood
BUILD_TXT := candidate azimu
BUILDS = $(BUILD_TIF) $(BUILD_TXT)

SCRIPT := ./piv-test.py
OUTBASE := ./res
DATABASE := ./data
OUTPUT_TIF := $(OUTBASE)/output.tif
SHELL := /bin/bash
TMP_CONFIG_FILE := config_tmp.py
TMP_OUTPUT := /dev/null

FRAME_LIST = $(shell seq 0 $$(($(NUM_FRAMES)-1)))
SAMPLE_DIRS = $(addprefix $(OUTBASE)/, $(SAMPLES))

define mk_config_file
$(1)
@cp config_$(lastword $(subst /, ,$(*D))).py $(TMP_CONFIG_FILE)
@sed -ri "s~([^#]out_file\s+=\s+).*~\1'$@',~g" $(TMP_CONFIG_FILE)
@sed -ri "s/([^#]\s+number\s+=\s+).*/\11,/g" $(TMP_CONFIG_FILE)
@sed -ri "s/(\s+start\s+=\s+)[0-9]+/\1$(number)/g" $(TMP_CONFIG_FILE)
@sed -ri "s/(graph = ).*/\1'$(graph)'/g" $(TMP_CONFIG_FILE)
endef

all: $(BUILD_TIF) $(BUILD_TXT)
.PHONY: all plots

$(BUILD_TIF): % : $(SAMPLE_DIRS) $(foreach ff,$(FRAME_LIST), $(foreach dd,$(SAMPLE_DIRS), $(dd)/%_$(ff).tif))
$(BUILD_TXT): % : $(SAMPLE_DIRS) $(foreach ff,$(FRAME_LIST), $(foreach dd,$(SAMPLE_DIRS), $(dd)/%_$(ff).txt)) 
plots : $(addsuffix .png,$(basename $(foreach dd,$(SAMPLE_DIRS),$(wildcard $(dd)/*.txt))))

%.tif %.txt: $(lastword $(subst /, ,$(%D)))
	@echo $@
	$(eval graph=$(firstword $(subst _, ,$(*F))))
	$(eval number=$(lastword $(subst _, ,$(*F))))
	$(mk_config_file)
	@python $(SCRIPT) $(basename $(TMP_CONFIG_FILE)) 2> $(TMP_OUTPUT)
	@rm config_tmp.py*

%.png :
	@echo $@ 
	$(eval number=$(lastword $(subst _, ,$(*F))))
	$(eval sample=$(lastword $(subst /, ,$(*D))))
	@./tests/plot-rings.py $(DATABASE)/$(sample)/00$(number).tif $*.txt 2> $(TMP_OUTPUT)

$(SAMPLE_DIRS):
	mkdir -p $@

clean: cleansub
	$(eval empty=$(shell ls -A $(OUTBASE)))
	@if [ "$(empty)" == "" ]; then rm -rf $(OUTBASE); fi
cleansub: 
	rm -rf $(SAMPLE_DIRS)
.PHONY: clean
