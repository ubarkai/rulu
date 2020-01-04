import sys
sys.path[:0] = ['/Users/ubarkai/repos/rulu']

import logging
from pkg_resources import resource_filename  # @UnresolvedImport
from unittest import TestCase
from rulu.builtin_aggregations import UNIQUE_INDEX_FIELD
from rulu.engine import RuleEngine
from rulu.slots import HasSlots

from . import inputs
from . import expected_outputs
from . import ruledefs
from .ruledefs import nearest_distance_rules

logging.basicConfig(level=logging.DEBUG)


class BaseRuleEngineTest(TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    def _engine_test(self, ruledef, input, expected_output=None):  # @ReservedAssignment
        engine = self._make_engine(ruledef)
        engine.load(resource_filename(inputs.__name__, input))
        engine.run_one_cycle()
        actual_facts = self._get_facts(engine)

        if expected_output is not None:
            engine2 = self._make_engine(ruledef)
            engine2.load(resource_filename(inputs.__name__, input))
            engine2.load(resource_filename(expected_outputs.__name__, expected_output))
            expected_facts = self._get_facts(engine2)
            self.assertEqual(expected_facts, actual_facts)
        return engine

    def _make_engine(self, ruledef):
        engine = RuleEngine()
        engine.load_module(ruledef, ruledefs)
        return engine

    def _get_facts(self, engine):
        res = []
        for fact in engine.get_all_facts():
            values = fact._as_dict()
            values.pop('_id', None)
            values.pop(UNIQUE_INDEX_FIELD, None)
            for key, value in values.items():
                if isinstance(value, HasSlots):
                    values[key] = value._as_dict()
            res.append('{} / {}'.format(fact._name, values))
        return sorted(res)



class RuleEngineTests(BaseRuleEngineTest):
    maxDiff = None
    
    def testFamily(self):
        self._engine_test(ruledef='family', input='fathers.txt', expected_output='grandfathers.txt')
        
    def testFamilyPython(self):
        self._engine_test(ruledef='family_python', input='fathers.txt', expected_output='grandfathers.txt')
        
    def testFamilyPythonFunc(self):
        self._engine_test(ruledef='family_func', input='fathers.txt', expected_output='grandfathers.txt')
        
    def testPythonFuncError(self):
        def testWithError():
            self._engine_test(ruledef='family_python_error', input='fathers.txt', expected_output=None)
        self.assertRaises(RuntimeError, testWithError)
        
    def testPythonAggregator(self):
        self._engine_test(ruledef='python_aggregations', input='pairs.txt', expected_output='aggregates.txt')
        
    def testBuiltinAggregator(self):
        self._engine_test(ruledef='builtin_aggregations', input='pairs.txt', expected_output='aggregates_with_count.txt')
        
    def testMultifield(self):
        self._engine_test(ruledef='multifield', input='pairs.txt', expected_output='concatenated.txt')
        
    def testUpdateDelete(self):
        self._engine_test(ruledef='update_delete', input='pairs.txt', expected_output='aggregates.txt')
        
    def testUpdateDeletePython(self):
        self._engine_test(ruledef='update_delete_python', input='pairs.txt', expected_output='aggregates.txt')

    def testMatchConst(self):
        self._engine_test(ruledef='match_const', input='consts.txt', expected_output='consts.txt')
        
    def testClassesWithPythonFunc(self):
        nearest_distance_rules.make_rule = nearest_distance_rules.python_func_distance_rule
        self._engine_test(ruledef='nearest', input='points.txt', expected_output='nearest.txt')
        
    def testClassesWithPythonRule(self):
        nearest_distance_rules.make_rule = nearest_distance_rules.python_distance_rule
        self._engine_test(ruledef='nearest', input='points.txt', expected_output='nearest.txt')
        
    def testClassesPythonFree(self):
        nearest_distance_rules.make_rule = nearest_distance_rules.python_free_distance_rule
        self._engine_test(ruledef='nearest', input='points.txt', expected_output='nearest.txt')
