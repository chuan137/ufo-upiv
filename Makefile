
.Phony: data filters

data:
	$(MAKE) -C data

plots:
	@cd data; make plots; cd ..

filters:
	$(MAKE) -C filters
