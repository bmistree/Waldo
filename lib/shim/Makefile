# A generic Makefile for a basic Waldo project that just needs to run
# the compiler over .wld files. .wld files get mapped maps %.wld ->
# %_v2.py or $_v4.py to avoid conflicts. Be careful how you name your
# driver .py files so they don't conflict!

# := means expand out now rather than when used
PROTOCOL_FILES := $(wildcard *.wld)
GENERATED_FILES := $(PROTOCOL_FILES:.wld=_v4.py)
COMPILE_ARGS= 
WCOMPILE_COMMAND = ../../bin/wcompile.py

.PHONY : v4
v4 : $(GENERATED_FILES)

# Says create a separate rule for each item in the GENERATED_FILES_V4
# list.  That rule should say take the item that ends in _v4.py and
# say that it depends on the same prefix, but with ending .wld.
# @see Static Pattern Rules
$(GENERATED_FILES) : %_v4.py : %.wld
	$(WCOMPILE_COMMAND) $(COMPILE_ARGS) -f $< -e $@


.PHONY : clean
clean :
	rm -f $(GENERATED_FILES) emitted_v4.py *.pyc parser.out parsetab.py *.pyo
