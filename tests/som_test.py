import unittest
from parameterized import parameterized
from som.vm.universe import Universe


class SomTest(unittest.TestCase):
    @parameterized.expand([
        ("ClassStructure",),
        ("Array"         ,),
        ("Block"         ,),
        ("ClassLoading"  ,),

        ("Closure"       ,),
        ("Coercion"      ,),
        ("CompilerReturn",),
        ("Double"        ,),

        ("Empty"         ,),
        ("Hash"          ,),
        ("Integer"       ,),
        ("ObjectSize"    ,),

        ("Preliminary"   ,),
        ("Reflection"    ,),
        ("SelfBlock"     ,),
        ("Super"         ,),

        ("String"        ,),
        ("Symbol"        ,),
        ("System"        ,),
        ("Vector"        ,)])
    def test_som_test(self, test_name):
        args = ["-cp", "Smalltalk", "TestSuite/TestHarness.som", test_name]
        u = Universe(True)
        u.interpret(args)
        
        self.assertEquals(0, u.last_exit_code())

import sys

if 'pytest' in sys.modules:
    # hack to make pytest not to collect the unexpanded test method
    delattr(SomTest, "test_som_test")
