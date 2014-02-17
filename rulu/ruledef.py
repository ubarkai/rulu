from bunch import Bunch
from functools import wraps

from aggregations import groupby
from expr import ConvertibleToExpr
from fact import FactReference
from rule import Rule

class RuleDef(FactReference, ConvertibleToExpr):
    _all_instances = []
    def __init__(self, *modifiers):
        self._rule = Rule()
        for modifier in modifiers:
            modifier(self._rule)
        self._fields = dict(self._rule.get_target_fields() or {})
        self.__dict__.update(self._fields)
        self._all_instances.append(self)
        
    def _set_name(self, name):
        self._rule.set_name(name)
        
    def _build(self, engine):
        self._rule.build(engine)
        
    def _python_action(self, function):
        self._rule.add_python_action(function)
        
    def _aggregator(self, aggregator_cls):
        self._rule.add_aggregator_cls(aggregator_cls)
        
    def _groupby(self, *keys):
        return lambda func : self._rule.add_aggregator_cls(groupby(keys, func))
    
    def __getitem__(self, key):
        return self._rule.target[key]
    
    def _to_expr(self):
        return self._rule.target._to_expr()
    
    @property
    def _name(self):
        return self._rule.get_target_name()
    
    def _update_python_param(self, params, value):
        return self._rule.target._update_python_param(params, value)

    def _from_python_params(self, params):
        return self._rule.target._from_python_params(params)

def rule_modifier(method):
    def modifier(*args, **kwargs):
        return wraps(method)(lambda rule : method(rule, *args, **kwargs))
    return modifier

match = rule_modifier(Rule.add_variable)
action = rule_modifier(Rule.add_action)
condition = rule_modifier(Rule.add_condition)
not_exists = rule_modifier(Rule.set_negative_premise)
fields = rule_modifier(Rule.set_target_fields)
salience = rule_modifier(Rule.set_salience)
name = rule_modifier(Rule.set_name)
description = rule_modifier(Rule.set_description)

@rule_modifier
def target(rule, target):
    if isinstance(target, RuleDef):
        target = target._rule.target
    rule.set_target(target)

@rule_modifier
def foreach(rule, *containers):
    for container in containers:
        rule.set_premise(container)

# Parameters passed from outside world to rule defintions
params = Bunch()

def delayed_set(field, from_value, to_value):
    from actions import Update
    RuleDef(
        condition(field == from_value),
        salience(-1000),
        action(Update(field.container, **{field.name: to_value}))
    )._set_name('AutoSet_{}'.format(field.name)),
