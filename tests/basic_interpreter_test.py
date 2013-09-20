import unittest
from parameterized import parameterized

from som.vm.universe       import Universe

from som.vmobjects.integer import Integer
from som.vmobjects.clazz   import Class

class BasicInterpreterTest(unittest.TestCase):
    @parameterized.expand([
        ("MethodCall",     "test",  42, Integer ),
        ("MethodCall",     "test2", 42, Integer ),

        ("NonLocalReturn", "test",  "NonLocalReturn", Class ),
        ("NonLocalReturn", "test1", 42, Integer ),
        ("NonLocalReturn", "test2", 43, Integer ),
        ("NonLocalReturn", "test3",  3, Integer ),
        ("NonLocalReturn", "test4", 42, Integer ),
        ("NonLocalReturn", "test5", 22, Integer ),

        ("Blocks", "arg1",  42, Integer ),
        ("Blocks", "arg2",  77, Integer ),
        ("Blocks", "argAndLocal",    8, Integer ),
        ("Blocks", "argAndContext",  8, Integer ),

        ("Return", "returnSelf",           "Return", Class ),
        ("Return", "returnSelfImplicitly", "Return", Class ),
        ("Return", "noReturnReturnsSelf",  "Return", Class ),
        ("Return", "blockReturnsImplicitlyLastValue", 4, Integer )])
    def test_basic_interpreter_behavior(self, test_class, test_selector, expected_result, result_type):
        u = Universe()
        u.setup_classpath("Smalltalk:TestSuite/BasicInterpreterTests")
        
        actual_result = u.execute_method(test_class, test_selector)
        
        self._assertEqualsSOMValue(expected_result, actual_result, result_type)
    
    def _assertEqualsSOMValue(self, expected_result, actual_result, result_type):
        if result_type is Integer:
            self.assertEquals(expected_result, actual_result.get_embedded_integer())
            return
        
        if result_type is Class:
            self.assertEquals(expected_result, actual_result.get_name().get_string())
            return

        self.fail("SOM Value handler missing")

import sys
if sys.modules.has_key('pytest'):
    # hack to make pytest not to collect the unexpanded test method
    delattr(BasicInterpreterTest, "test_basic_interpreter_behavior")