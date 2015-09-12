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
from utils import LispExpr


class ActivationLogReader(object):
    """
    Reader for the rule activation log.
    """
    def __init__(self, engine):
        self.engine = engine
        self.environment = engine.environment
        self.clear()

    def clear(self):
        clips.TraceStream.Read()

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
        activation_re = re.compile('>>> ([\w\d@]+) ((?:\d+ )+)=(.+)$')
        fact_index_re = re.compile('<Fact-(\d+)>')
        for line in clips.TraceStream.Read().splitlines():
            rule_name, src_fact_ids, target_fact = activation_re.match(line).groups()
            if target_fact == 'FALSE':
                continue
            rule = self.rule_by_name[rule_name]
            src_facts = [self.fact_by_index[int(fact_id)] for fact_id in src_fact_ids.split()]
            match = fact_index_re.match(target_fact)
            target_fact = self.fact_by_index[int(match.group(1))] if match else None
            yield rule, src_facts, target_fact
            
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


def _add_trace_to_actions(rule_name, source_premises, actions_lisp):
    # Using custom prints instead of standard CLIPS activations log, which does not link activations to asserted facts
    for n, action in enumerate(actions_lisp):
        print_args = ['">>> "', '"'+rule_name+' "']
        for premise in source_premises.values():
            if not premise.negative:
                print_args.extend([LispExpr("fact-index", premise.var_name), '" "'])
        print_args.extend(["=", action])
        if action.values[0] in ('modify', 'delete'):
            print_args.append(LispExpr('fact-index', actions_lisp[0].values[1]))
        print_args.append('crlf')
        actions_lisp[n] = LispExpr('printout', 'wtrace', *print_args)
