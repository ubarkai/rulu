PYTHON=PYTHONPATH=.:ruledefs python

.PHONY: rulu ruledefs_from_unittests run_examples

all: rulu

rulu: ruledefs_from_unittests run_examples

ruledefs_from_unittests: ruledefs/family.py

ruledefs/%.py: ../test/ruledefs/%.py
	cp $< $@
    
run_examples: family-out.txt family-out.clp greeting-out.txt

family-out.txt: basic_example.py
	$(PYTHON) $< > $@

family-out.clp: save_load.py family-in.clp
	$(PYTHON) $<

greeting-out.txt: clips_funcs.py
	$(PYTHON) $<
