"""
This module provides a mechanism for tracing the rules activated by the rule
engine, including source and asserted facts for each activation.

Note: facts asserted from Python code are currently not included in the trace.
"""

import clips
import re
from collections import defaultdict

from actions import Assert
from expr import BaseExpr
from ruledef import RuleDef

class ActivationLogReader(object):
    """
    Reader for the rule activation log.
    
    Note: for this to work, the engine must be initialized with trace=True.
    """
    def __init__(self, engine):
        self.engine = engine
        self.environment = engine.environment
        self._read_facts()
        self._read_rules()
        
    def find_fact(self, fact_type, **kwargs):
        """
        Find a fact object by type and field values
        """
        for key, value in kwargs.items():
            if isinstance(value, BaseExpr):
                kwargs[key] = value.evaluate()
        values = tuple(value.evaluate() if isinstance(value, BaseExpr) else value for _, value in 
                       sorted(kwargs.iteritems(), key=lambda x:fact_type._field_order[x[0]]))
        return self.fact_by_content[fact_type._name][values]        

    def get_activations(self):
        """
        Return an iterator over the activation log, including rule object and
        source facts for each activation
        """
        ACTIVATION_RE = re.compile('==> Activation 0\s+([\w@]+): ([f\-\d\,]+)')
        for line in clips.TraceStream.Read().splitlines():
            rule_name, src_fact_ids = ACTIVATION_RE.match(line).groups()
            rule = self.rule_by_name[rule_name]
            src_facts = [self.fact_by_index[int(fact_id.rsplit('-', 1)[1])]
                         for fact_id in src_fact_ids.split(',')]
            yield rule, src_facts
            
    def resolve_asserted_facts(self, rule, src_facts):
        """
        Find the facts that are asserted (using the Assert action) by a given rule 
        and specific source facts. 
        """
        field_map = {}
        fact_map = {}
        premises = rule.premises.values()
        premises.sort(key=lambda p:p.var_name)
        for premise, fact in zip(premises, src_facts):
            premise.container._update_python_param(fact_map, fact)
            for key, value in fact._as_dict().iteritems():
                field_map[getattr(premise.container, key)] = value

        asserted_data = []
        for action in rule.actions:
            if isinstance(action, Assert):
                asserted_data.append(action.replace_fields(field_map).data)
                
        for action in rule.python_actions:
            assert_ = lambda **kwargs: asserted_data.append(kwargs)
            action(assert_=assert_, **fact_map)
            
        for data in asserted_data:
            yield self.find_fact(rule.target, **data)

    def _read_facts(self):
        """ Read and index all facts. """
        self.fact_by_index = {}
        self.fact_by_content = defaultdict(dict)
        for fact in self.engine.get_facts():
            self.fact_by_index[fact._clips_obj.Index] = fact
            self.fact_by_content[fact._name][fact._data] = fact
    
    def _read_rules(self):
        self.rule_by_name = {rule_def._rule.clips_name: rule_def._rule
                             for rule_def in RuleDef._all_instances}
