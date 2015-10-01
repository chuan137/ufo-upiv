SHELL := /bin/bash

#SAMPLES := sampleB sampleC
SAMPLES := sampleB
FRAMES := 3

TARGETDIR = data/res/
CONFIGFILE = config_tmp.py
INPUTPATH = data/
OUTFILE = data/res_tmp.tif

all : hough likelyhood

.PHONY : tests all

define run_single
@for sample in $(SAMPLES); do \
	cp config_$$sample.py $(CONFIGFILE); \
	mkdir -p $(TARGETDIR)/$$sample; \
	sed -ri "s/(graph = )[0-9]/\1\(2)/g" $(CONFIGFILE); \
	sed -ri "s~([^#]in_path\s+=\s+).*~\1'$(INPUTPATH)/$$sample',~g" $(CONFIGFILE); \
	sed -ri "s~([^#]out_file\s+=\s+).*~\1'$(OUTFILE)',~g" $(CONFIGFILE); \
	for key in `seq 1 $(FRAMES)`; do \
		key=$$(( $$key - 1 )); \
		sed -ri "s/(\s+start\s+=\s+)[0-9]+/\1$$key/g" $(CONFIGFILE); \
		python ./piv.py $(CONFIGFILE); \
		cp $(OUTFILE) $(TARGETDIR)/$$sample/$(strip $(1))_$$key.tif; \
		done \
	done
endef

define run_series
@for sample in $(SAMPLES); do \
	cp config_$$sample.py $(CONFIGFILE); \
	mkdir -p $(TARGETDIR)/$$sample; \
	sed -ri "s/(graph = )[0-9]/\1\(2)/g" $(CONFIGFILE); \
	sed -ri "s~([^#]in_path\s+=\s+).*~\1'$(INPUTPATH)/$$sample',~g" $(CONFIGFILE); \
	sed -ri "s~([^#]out_file\s+=\s+).*~\1'$(OUTFILE)',~g" $(CONFIGFILE); \
	sed -ri "s/([^#]\s+number\s+=\s+).*/\1$(FRAMES),/g" $(CONFIGFILE); \
	python ./piv.py $(CONFIGFILE); \
	cp $(OUTFILE) $(TARGETDIR)/$$sample/$(strip $(1)).tif; \
	rm $(CONFIGFILE)*; \
	done
endef


tests :	
	@echo $(sampleB_ROOT)

hough : config.py
	@echo $@
	$(call run_single, $@, 3)

likelyhood : config.py
	@echo $@
	@cp $< $(CONFIGFILE)
	@sed -ri "s/(graph = )[0-9]/\12/g" $(CONFIGFILE)
	$(call run_single, $@)
	@rm $(CONFIGFILE)*
