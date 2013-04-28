
PROTOCOL_FILES := $(wildcard *.proto)
GENERATED_FILES := $(PROTOCOL_FILES:.proto=_pb2.py)
COMPILE_FOLDER := ../proto_compiled/

.PHONY : all_proto
all_proto : $(GENERATED_FILES)

$(GENERATED_FILES) : %_pb2.py : %.proto
	protoc -I=. --python_out=$(COMPILE_FOLDER) $<

.PHONY : clean
clean :
	rm $(COMPILE_FOLDER)/*_pb2.py
