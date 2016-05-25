#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from som.vm.universe import main, Exit
from som.interpreter.control_flow import ReturnException

import os

# __________  Entry points  __________

def entry_point(argv):
    try:
        main(argv)
    except Exit, e:
        return e.code
    except ReturnException, e:
        os.write(2, "ERROR: Caught ReturnException in entry_point. result: %s, target: %s\n" %
                 (e._result, e._target))
        return 1
    except Exception, e:
        os.write(2, "ERROR: Exception thrown during execution: " + str(e) + "\n")
        return 1
    os.write(2, "ERROR: Program exited without raising the Exit exception.\n")
    return 1


# _____ Define and setup target ___


def target(driver, args):
    if driver.config.translation.jit:
        driver.exe_name = 'RPySOM-jit'
    else:
        driver.exe_name = 'RPySOM-no-jit'
    return entry_point, None


def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()


if __name__ == '__main__':
    from rpython.translator.driver import TranslationDriver
    f, _ = target(TranslationDriver(), sys.argv)
    sys.exit(f(sys.argv))
