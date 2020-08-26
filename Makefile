#!/usr/bin/env make -f

PYPY_DIR ?= pypy
RPYTHON  ?= $(PYPY_DIR)/rpython/bin/rpython


all: compile

# RPySOM-no-jit
compile: RPySOM-jit

RPySOM-no-jit:
	PYTHONPATH=$(PYTHONPATH):$(PYPY_DIR) $(RPYTHON) --batch src/main-rpython.py

RPySOM-jit:	
	PYTHONPATH=$(PYTHONPATH):$(PYPY_DIR) $(RPYTHON) --batch -Ojit src/main-rpython.py

test: compile
	PYTHONPATH=$(PYTHONPATH):$(PYPY_DIR) nosetests
	#./RPySOM-no-jit -cp Smalltalk TestSuite/TestHarness.som
	./RPySOM-jit    -cp Smalltalk TestSuite/TestHarness.som

clean:
	@-rm RPySOM-no-jit
	@-rm RPySOM-jit
