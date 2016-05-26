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
    return 0


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
