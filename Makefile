#!/usr/bin/env make -f

PYPY_DIR ?= pypy
RPYTHON  ?= $(PYPY_DIR)/rpython/bin/rpython


all: compile

# RTruffleSOM-no-jit 
compile: RTruffleSOM-jit

RTruffleSOM-no-jit: core-lib/.git
	PYTHONPATH=$(PYTHONPATH):$(PYPY_DIR) $(RPYTHON) --batch src/targetsomstandalone.py

RTruffleSOM-jit: core-lib/.git
	PYTHONPATH=$(PYTHONPATH):$(PYPY_DIR) $(RPYTHON) --batch -Ojit src/targetsomstandalone.py

test: compile core-lib/.git
	PYTHONPATH=$(PYTHONPATH):$(PYPY_DIR) nosetests
	if [ -e ./RTruffleSOM-no-jit ]; then ./RTruffleSOM-no-jit -cp Smalltalk TestSuite/TestHarness.som; fi
	if [ -e ./RTruffleSOM-jit ];    then ./RTruffleSOM-jit    -cp Smalltalk TestSuite/TestHarness.som; fi

clean:
	@-rm RTruffleSOM-no-jit
	@-rm RTruffleSOM-jit

core-lib/.git:
	git submodule update --init
