"""
This module defines the possible actions that can be used in rule activations. 
"""

from .expr import normalize_expr, BaseExpr
from .utils import LispExpr, RuleEngineError
from functools import reduce


class BaseAction(BaseExpr):
    """
    Base class for rule actions
    """
    def prepare_rule(self, rule):
        """ Hook for manipulating any rule that contains the current action """
        pass
    
    def get_type(self):
        # Actions can't be used as expressions. 
        return None


class AssertOrUpdate(BaseAction):
    """
    Base class for actions that deal with data values (assert / update)
    """
    def __init__(self, **data):
        super().__init__()
        self.data = {key : normalize_expr(value) for key, value in data.items()}

    def get_all_fields(self):
        return reduce(set.union, (v.all_fields for v in self.data.values()), set())
                
    def _replace_fields(self, field_map):
        return {key: value.replace_fields(field_map) for key, value in self.data.items()}
    
    def _field_values_to_lisp(self):
        return [LispExpr(key, value.to_lisp()) for key, value in sorted(self.data.items())]


class Assert(AssertOrUpdate):
    """ 
    Defines the most common action: assert (i.e., create) a new fact with given field values.
    If a target template is not defined for the rule, we automatically create one,
    deducing its fields from the Assert parameters.
    """

    def __init__(self, target=None, **data):
        super().__init__(**data)
        self.rule = None
        self.target = target

    def replace_fields(self, field_map):
        res = Assert(target=self.target, **self._replace_fields(field_map))
        res.rule = self.rule
        return res
    
    def prepare_rule(self, rule):
        if self.rule is not None:
            raise RuleEngineError('"Assert" instance may only be used in a single rule.')
        self.rule = rule

        # Deduce fields for rule target
        if rule.target is None and self.target is None and rule.target_fields is None:
            implied_fields = {key:value.get_type() for key, value in self.data.items()}
            rule.set_target_fields(**implied_fields)
        # Fields of input facts cannot be used directly in the Assert() clause.
        # They must be bound to variables.
        for key, value in self.data.items():
            for field in value.all_fields:
                rule.add_variable(field)
        
    def to_lisp(self):
        field_values = self._field_values_to_lisp()
        target_name = self.target._name if self.target is not None else self.rule.get_target_name()
        return LispExpr('assert', LispExpr(target_name, *field_values))

    def __str__(self):
        return 'Assert({})'.format(', '.join('{}={}'.format(k, v) for k, v in sorted(self.data.items())))


class Update(AssertOrUpdate):
    """ 
    Defines an action that updates one of the rule's input facts with given field values
    """

    def __init__(self, _fact, **data):
        super().__init__(**data)
        self.fact = _fact

    def replace_fields(self, field_map):
        return Update(field_map[self.fact._to_expr()], **self._replace_fields(field_map))
    
    def to_lisp(self):
        field_values = self._field_values_to_lisp()
        return LispExpr('modify', self.fact, *field_values)
    

class Delete(BaseAction):
    """ Defines an action that deletes (retracts) one of the rule's input facts """
     
    def __init__(self, _fact):
        super().__init__()
        self.fact = _fact
        
    def get_all_fields(self):
        return set()

    def replace_fields(self, field_map):
        return Delete(field_map[self.fact._to_expr()])

    def to_lisp(self):
        return LispExpr('retract', self.fact)
