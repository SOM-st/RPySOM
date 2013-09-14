# Source: https://github.com/wolever/nose-parameterized
# commit 0da3a2f0325c17858a5f5f1fdf1939520ce85e48, Aug 25, 2013
# Stefan: I removed the dependency on the six module, don't need the portability, now.
# 
# tl;dr: all code code is licensed under simplified BSD, unless stated otherwise.
# 
# Unless stated otherwise in the source files, all code is copyright 2010 David
# Wolever <david@wolever.net>. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
#    1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 
#    2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY <COPYRIGHT HOLDER> ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL <COPYRIGHT HOLDER> OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of David Wolever.

import re
import inspect
from functools import wraps
from collections import namedtuple

from nose.tools import nottest
from unittest import TestCase

import new
new_instancemethod = new.instancemethod

_param = namedtuple("param", "args kwargs")

class param(_param):
    """ Represents a single parameter to a test case.

        For example::

            >>> p = param("foo", bar=16)
            >>> p
            param("foo", bar=16)
            >>> p.args
            ('foo', )
            >>> p.kwargs
            {'bar': 16}

        Intended to be used as an argument to ``@parameterized``::

            @parameterized([
                param("foo", bar=16),
            ])
            def test_stuff(foo, bar=16):
                pass
        """

    def __new__(cls, *args , **kwargs):
        return _param.__new__(cls, args, kwargs)

    @classmethod
    def explicit(cls, args=None, kwargs=None):
        """ Creates a ``param`` by explicitly specifying ``args`` and
            ``kwargs``::

                >>> param.explicit([1,2,3])
                param(*(1, 2, 3))
                >>> param.explicit(kwargs={"foo": 42})
                param(*(), **{"foo": "42"})
            """
        args = args or ()
        kwargs = kwargs or {}
        return cls(*args, **kwargs)

    @classmethod
    def from_decorator(cls, args):
        """ Returns an instance of ``param()`` for ``@parameterized`` argument
            ``args``::

                >>> param.from_decorator((42, ))
                param(args=(42, ), kwargs={})
                >>> param.from_decorator("foo")
                param(args=("foo", ), kwargs={})
            """
        if isinstance(args, param):
            return args
        if isinstance(args, basestring):
            args = (args, )
        return cls(*args)

    def __repr__(self):
        return "param(*%r, **%r)" %self

class parameterized(object):
    """ Parameterize a test case::

            class TestInt(object):
                @parameterized([
                    ("A", 10),
                    ("F", 15),
                    param("10", 42, base=42)
                ])
                def test_int(self, input, expected, base=16):
                    actual = int(input, base=base)
                    assert_equal(actual, expected)

            @parameterized([
                (2, 3, 5)
                (3, 5, 8),
            ])
            def test_add(a, b, expected):
                assert_equal(a + b, expected)
        """

    def __init__(self, input):
        self.get_input = self.input_as_callable(input)

    def __call__(self, test_func):
        self.assert_not_in_testcase_subclass()

        @wraps(test_func)
        def parameterized_helper_method(test_self=None):
            f = test_func
            if test_self is not None:
                # If we are a test method (which we suppose to be true if we
                # are being passed a "self" argument), we first need to create
                # an instance method, attach it to the instance of the test
                # class, then pull it back off to turn it into a bound method.
                # If we don't do this, Nose gets cranky.
                f = self.make_bound_method(test_self, test_func)
            # Note: because nose is so very picky, the more obvious
            # ``return self.yield_nose_tuples(f)`` won't work here.
            for nose_tuple in self.yield_nose_tuples(f):
                yield nose_tuple

        test_func.__name__ = "_helper_for_%s" %(test_func.__name__, )
        parameterized_helper_method.parameterized_input = input
        parameterized_helper_method.parameterized_func = test_func
        return parameterized_helper_method

    def yield_nose_tuples(self, func):
        for args in self.get_input():
            p = param.from_decorator(args)
            # ... then yield that as a tuple. If those steps aren't
            # followed precicely, Nose gets upset and doesn't run the test
            # or doesn't run setup methods.
            yield self.param_as_nose_tuple(p, func)

    def param_as_nose_tuple(self, p, func):
        nose_func = func
        nose_args = p.args
        if p.kwargs:
            nose_func = wraps(func)(lambda args, kwargs: func(*args, **kwargs))
            nose_args = (p.args, p.kwargs)
        return (nose_func, ) + nose_args

    def make_bound_method(self, instance, func):
        cls = type(instance)
        im_f = new_instancemethod(func, None, cls)
        setattr(cls, func.__name__, im_f)
        return getattr(instance, func.__name__)

    def assert_not_in_testcase_subclass(self):
        parent_classes = self._terrible_magic_get_defining_classes()
        if any(issubclass(cls, TestCase) for cls in parent_classes):
            raise Exception("Warning: '@parameterized' tests won't work "
                            "inside subclasses of 'TestCase' - use "
                            "'@parameterized.expand' instead")

    def _terrible_magic_get_defining_classes(self):
        """ Returns the set of parent classes of the class currently being defined.
            Will likely only work if called from the ``parameterized`` decorator.
            This function is entirely @brandon_rhodes's fault, as he suggested
            the implementation: http://stackoverflow.com/a/8793684/71522
            """
        stack = inspect.stack()
        if len(stack) <= 4:
            return []
        frame = stack[4]
        code_context = frame[4] and frame[4][0].strip()
        if not (code_context and code_context.startswith("class ")):
            return []
        _, parents = code_context.split("(", 1)
        parents, _ = parents.rsplit(")", 1)
        return eval("[" + parents + "]", frame[0].f_globals, frame[0].f_locals)

    @classmethod
    def input_as_callable(cls, input):
        if callable(input):
            return lambda: cls.check_input_values(input())
        input_values = cls.check_input_values(input)
        return lambda: input_values

    @classmethod
    def check_input_values(cls, input_values):
        if not hasattr(input_values, "__iter__"):
            raise ValueError("expected iterable input; got %r" %(input, ))
        return input_values

    @classmethod
    def expand(cls, input):
        """ A "brute force" method of parameterizing test cases. Creates new
            test cases and injects them into the namespace that the wrapped
            function is being defined in. Useful for parameterizing tests in
            subclasses of 'UnitTest', where Nose test generators don't work.

            >>> @parameterized.expand([("foo", 1, 2)])
            ... def test_add1(name, input, expected):
            ...     actual = add1(input)
            ...     assert_equal(actual, expected)
            ...
            >>> locals()
            ... 'test_add1_foo_0': <function ...> ...
            >>>
            """

        def parameterized_expand_wrapper(f):
            stack = inspect.stack()
            frame = stack[1]
            frame_locals = frame[0].f_locals

            base_name = f.__name__
            get_input = cls.input_as_callable(input)
            for num, args in enumerate(get_input()):
                p = param.from_decorator(args)
                name_suffix = "_%s" %(num, )
                if len(p.args) > 0 and isinstance(p.args[0], basestring):
                    name_suffix += "_" + cls.to_safe_name(p.args[0])
                name = base_name + name_suffix
                frame_locals[name] = cls.param_as_standalone_func(p, f, name)
            return nottest(f)
        return parameterized_expand_wrapper

    @classmethod
    def param_as_standalone_func(cls, p, func, name):
        standalone_func = lambda *a: func(*(a + p.args), **p.kwargs)
        standalone_func.__name__ = name
        return standalone_func

    @classmethod
    def to_safe_name(cls, s):
        return str(re.sub("[^a-zA-Z0-9_]", "", s))
