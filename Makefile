#!/usr/bin/env make -f

all: compile

compile: RPySOM-no-jit RPySOM-jit

RPySOM-no-jit:
	PYTHONPATH=$PYTHONPATH:pypy pypy/rpython/bin/rpython --batch src/targetsomstandalone.py

RPySOM-jit:	
	PYTHONPATH=$PYTHONPATH:pypy pypy/rpython/bin/rpython --batch -Ojit src/targetsomstandalone.py

test: compile
	PYTHONPATH=$PYTHONPATH:pypy nosetests
	./RPySOM-no-jit -cp Smalltalk TestSuite/TestHarness.som
	./RPySOM-jit    -cp Smalltalk TestSuite/TestHarness.som

clean:
	@-rm RPySOM-no-jit
	@-rm RPySOM-jit
