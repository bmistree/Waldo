# A generic Makefile for a basic Waldo project that just needs to run
# the compiler over .wld files. For simple projects, it compiles to
# emitted.py, the default provided when no output filename is
# specified. For multiple .wld files it maps %.wld -> %.py to avoid
# conflicts. Be careful how you name your driver .py files so they
# don't conflict!
#
# BE CAREFUL editing this since it's symlinked to a bunch of examples.

PROTOCOL_FILES := $(wildcard *.wld)
GENERATED_FILES := $(PROTOCOL_FILES:.wld=.py)

# Make 1 wld file compile to emitted.py for simplicity/generic
# top-level gitignore for generated files. Two or more you have to
# deal with manually
ifeq ($(words $(PROTOCOL_FILES)), 1)
REAL_OUTPUT := emitted.py

.PHONY : all
all : $(REAL_OUTPUT)

# No -e => emitted.py
emitted.py : $(PROTOCOL_FILES)
	../../bin/wcompile.py -f $<
else
REAL_OUTPUT := $(GENERATED_FILES)

.PHONY : all
all : $(REAL_OUTPUT)

$(GENERATED_FILES) : %.py : %.wld
	../../bin/wcompile.py -f $< -e $@
endif

.PHONY : clean
clean :
	rm -f $(REAL_OUTPUT)
