#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from som.vm.universe import main, Exit

import os

# __________  Entry points  __________


def entry_point(argv):
    try:
        main(argv)
    except Exit, e:
        return e.code
    except Exception, e:
        os.write(2, "ERROR: %s thrown during execution.\n" % e)
        return 1
    return 1


# _____ Define and setup target ___


def target(driver, args):
    interp_type = os.getenv('SOM_INTERP', None)
    if interp_type is None or not (interp_type == 'AST' or interp_type == 'BC'):
        print("Type of interpreter not set. Please set the SOM_INTERP environment variable")
        print("\tSOM_INTERP=AST   Use an Abstract Syntax Tree interpreter")
        print("\tSOM_INTERP=BC    Use a Bytecode interpreter")
        sys.exit(1)

    exe_name = 'som-'
    if interp_type == 'AST':
        exe_name += 'ast-'
    elif interp_type == 'BC':
        exe_name += 'bc-'

    if driver.config.translation.jit:
        exe_name += 'jit'
    else:
        exe_name += 'interp'

    driver.exe_name = exe_name
    return entry_point, None


def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()


if __name__ == '__main__':
    from rpython.translator.driver import TranslationDriver
    f, _ = target(TranslationDriver(), sys.argv)
    sys.exit(f(sys.argv))
