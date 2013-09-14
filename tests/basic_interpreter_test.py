import unittest
from parameterized import parameterized

class BasicInterpreterTest(unittest.TestCase):
    @parameterized.expand([
        ("MethodCall",     "test",  42, Integer ),
        ("MethodCall",     "test2", 42, Integer ),

        ("NonLocalReturn", "test",  "NonLocalReturn", som.vmobjects.Class ),
        ("NonLocalReturn", "test1", 42, Integer ),
        ("NonLocalReturn", "test2", 43, Integer ),
        ("NonLocalReturn", "test3",  3, Integer ),
        ("NonLocalReturn", "test4", 42, Integer ),
        ("NonLocalReturn", "test5", 22, Integer ),

        ("Blocks", "arg1",  42, Integer ),
        ("Blocks", "arg2",  77, Integer ),
        ("Blocks", "argAndLocal",    8, Integer ),
        ("Blocks", "argAndContext",  8, Integer ),

        ("Return", "returnSelf",           "Return", som.vmobjects.Class ),
        ("Return", "returnSelfImplicitly", "Return", som.vmobjects.Class ),
        ("Return", "noReturnReturnsSelf",  "Return", som.vmobjects.Class ),
        ("Return", "blockReturnsImplicitlyLastValue", 4, Integer )
        ])
    def test_basic_interpreter_behavior(self, test_class, test_selector, expected_result, result_type):
        u = Universe()
        u.setup_classpath("Smalltalk:BasicInterpreterTests")
        
        actual_result = u.interpret(test_class, test_selector)
        
        self._assertEqualsSOMValue(expected_result, actual_result, result_type)
    
    def _assertEqualsSOMValue(self, expected_result, actual_result, result_type):
        if result_type is Integer:
            self.assertEquals(expected_result, actual_result.embedded_integer)
            return
        
        if result_type is som.vmobjects.Class:
            self.assertEquals(expected_result, actual_result.name.string)
            return

        self.fail("SOM Value handler missing")
