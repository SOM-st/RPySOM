import unittest
import sys
from parameterized import parameterized
from som.vm.universe import Universe


class SomTest(unittest.TestCase):
    @parameterized.expand([
        ("Array"         ,),
        ("Block"         ,),
        ("ClassLoading"  ,),
        ("ClassStructure",),

        ("Closure"       ,),
        ("Coercion"      ,),
        ("CompilerReturn",),
        ("DoesNotUnderstand",),
        ("Double"        ,),

        ("Empty"         ,),
        ("Global"        ,),
        ("Hash"          ,),
        ("Integer"       ,),

        ("Preliminary"   ,),
        ("Reflection"    ,),
        ("SelfBlock"     ,),
        ("SpecialSelectors",),
        ("Super"         ,),

        ("Set",),
        ("String"        ,),
        ("Symbol"        ,),
        ("System"        ,),
        ("Vector"        ,)])
    def test_som_test(self, test_name):
        args = ["-cp", "Smalltalk", "TestSuite/TestHarness.som", test_name]
        u = Universe(True)
        u.interpret(args)

        self.assertEquals(0, u.last_exit_code())


if 'pytest' in sys.modules:
    # hack to make pytest not to collect the unexpanded test method
    delattr(SomTest, "test_som_test")
