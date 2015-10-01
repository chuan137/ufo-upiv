SHELL := /bin/bash

#SAMPLES := sampleB sampleC
SAMPLES := sampleB
FRAMES := 1

frames := $$(seq 0 $$(($(FRAMES)-1)))

TARGETDIR = data/res/
CONFIGFILE = config_tmp.py
INPUTPATH = data/
OUTFILE = data/res_tmp.tif

all : hough likelyhood candidate

.PHONY : tests all

define run_single
@for sample in $(SAMPLES); do \
	if [ -n "$(3)" ]; then stdout="$(3)"; else stdout="/dev/null"; fi;\
	echo $$stdout; \
	cp config_$$sample.py $(CONFIGFILE); \
	mkdir -p $(TARGETDIR)/$$sample; \
	sed -ri "s/(graph = )[0-9]/\1$(2)/g" $(CONFIGFILE); \
	sed -ri "s~([^#]in_path\s+=\s+).*~\1'$(INPUTPATH)/$$sample',~g" $(CONFIGFILE); \
	sed -ri "s~([^#]out_file\s+=\s+).*~\1'$(OUTFILE)',~g" $(CONFIGFILE); \
	for key in $(frames); do \
		sed -ri "s/(\s+start\s+=\s+)[0-9]+/\1$$key/g" $(CONFIGFILE); \
		python ./piv.py $(CONFIGFILE) 1> $$stdout 2> /dev/null; \
		if [ -n "$(3)" ]; then \
			mv $$stdout $(TARGETDIR)/$$sample/$(strip $(3)).$$key; \
		else \
			mv $(OUTFILE) $(TARGETDIR)/$$sample/$(strip $(1))_$$key.tif; \
		fi \
		done \
	done
endef

define run_series
@for sample in $(SAMPLES); do \
	cp config_$$sample.py $(CONFIGFILE); \
	mkdir -p $(TARGETDIR)/$$sample; \
	sed -ri "s/(graph = )[0-9]/\1$(2)/g" $(CONFIGFILE); \
	sed -ri "s~([^#]in_path\s+=\s+).*~\1'$(INPUTPATH)/$$sample',~g" $(CONFIGFILE); \
	sed -ri "s~([^#]out_file\s+=\s+).*~\1'$(OUTFILE)',~g" $(CONFIGFILE); \
	sed -ri "s/([^#]\s+number\s+=\s+).*/\1$(FRAMES),/g" $(CONFIGFILE); \
	python ./piv.py $(CONFIGFILE); \
	cp $(OUTFILE) $(TARGETDIR)/$$sample/$(strip $(1)).tif; \
	rm $(CONFIGFILE)*; \
	done
endef


tests :	
	@echo $(frames)
	@echo $(foreach ss, $(SAMPLES), config_$(ss).py)

hough : $(foreach ss, $(SAMPLES), config_$(ss).py)
	@echo -e "\nBuilding $@ ..."
	$(call run_single, $@, 3)

likelyhood : $(foreach ss, $(SAMPLES), config_$(ss).py)
	@echo -e "\nBuilding $@ ..."
	$(call run_single, $@, 2)

candidate: $(foreach ss, $(SAMPLES), config_$(ss).py)
	@echo -e "\nBuilding $@ ..."
	$(call run_single, $@, 1, cand.txt)

.PHONY : clean

clean:
	rm -rf $(foreach ss, $(SAMPLES), $(TARGETDIR)/$(ss))
