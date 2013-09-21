#!/bin/sh
if [ -z "$PYTHON" ]; then
  PYTHON=python
fi
PYTHONPATH=src:$PYTHONPATH
exec $PYTHON src/som/vm/universe.py "$@"
