import unittest
from parameterized import parameterized

class SomTest(unittest.TestCase):
    @parameterized.expand([
        ("Array"         ,),
        ("BigInteger"    ,),
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

        ("Symbol"        ,),
        ("Vector"        ,)])
    def test_som_test(self, test_name):
        args = ["-cp", "Smalltalk", "TestSuite/TestHarness.som", test_name]
        u = Universe()
        u.interpret(args)
        
        self.assertEquals(0, u.last_exit_code)
