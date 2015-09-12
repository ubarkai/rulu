import clips
from test_ruleengine import BaseRuleEngineTest


class ActivationLogTests(BaseRuleEngineTest):
    def test_simple(self):
        engine = self._engine_test(ruledef='pair_sum', input='pairs.txt', trace=True)
        trace = list(engine.activation_log_reader.get_activations())
        self.assertEqual(len(trace), 5)
        self.assertItemsEqual([target_fact.sum for _, _, target_fact in trace], [2, 3, 4, 7, 9])
        for rule, source_facts, target_fact in trace:
            self.assertEqual(len(source_facts), 1)
            self.assertEqual(source_facts[0].first+source_facts[0].second, target_fact.sum)
