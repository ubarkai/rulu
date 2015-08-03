"""
This module provides a mechanism for tracing the rules activated by the rule
engine, including source and asserted facts for each activation.

Note: facts asserted from Python code are currently not included in the trace.
"""

import clips
import re
from collections import defaultdict
from contextlib import contextmanager

from actions import Assert
from expr import BaseExpr
from ruledef import RuleDef


class ActivationLogReader(object):
    """
    Reader for the rule activation log.
    """
    def __init__(self, engine):
        self.engine = engine
        self.environment = engine.environment

    def clear(self):
        clips.TraceStream.Read()
        self.environment.DebugConfig.ActivationsWatched = True
        self._python_assertion_trace = defaultdict(list)
        self._python_key = None

    def find_fact(self, fact_type, **kwargs):
        """
        Find a fact object by type and field values
        """
        for key, value in kwargs.items():
            if isinstance(value, BaseExpr):
                kwargs[key] = value.evaluate()
        values = tuple(value.evaluate() if isinstance(value, BaseExpr) else value for _, value in 
                       sorted(kwargs.iteritems(), key=lambda x: fact_type._field_order[x[0]]))
        return self.fact_by_content[fact_type._name].get(values)

    def get_activations(self):
        """
        Return an iterator over the activation log, including rule object and
        source facts for each activation
        """
        self._read_facts()
        self._read_rules()
        activation_re = re.compile('==> Activation (\-?\d+)\s+([\w@]+): ([f\-\d\,]+)')
        for line in clips.TraceStream.Read().splitlines():
            if line.startswith('<=='):
                continue
            salience, rule_name, src_fact_ids = activation_re.match(line).groups()
            rule = self.rule_by_name[rule_name]
            src_facts = [self.fact_by_index[int(fact_id.rsplit('-', 1)[1])]
                         for fact_id in src_fact_ids.split(',') if fact_id.startswith('f-')]
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

        for action in rule.actions:
            if isinstance(action, Assert):
                params = action.replace_fields(field_map).data
                fact = self.find_fact(rule.target, **params)
                if fact is not None:
                    yield fact

        for fact_id in self._python_assertion_trace[self._trace_key(rule, src_facts)]:
            yield self.fact_by_index[fact_id]


    def _read_facts(self):
        """ Read and index all facts. """
        self.fact_by_index = {}
        self.fact_by_content = defaultdict(dict)
        for fact in self.engine.get_all_facts():
            self.fact_by_index[fact._clips_obj.Index] = fact
            self.fact_by_content[fact._name][fact._data] = fact
    
    def _read_rules(self):
        self.rule_by_name = {rule_def._rule.clips_name: rule_def._rule
                             for rule_def in RuleDef._all_instances}

    @contextmanager
    def _trace_asserts(self, rule, facts):
        self._python_key = self._trace_key(rule, facts)
        yield
        self._python_key = None

    @staticmethod
    def _trace_key(rule, facts):
        return tuple([rule.name] + sorted(f._clips_index() for f in facts))

    def _add_python_assert(self, fact):
        self._python_assertion_trace[self._python_key].append(fact._clips_index())
