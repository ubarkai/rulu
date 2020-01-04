from functools import reduce
from .expr import BaseExpr, normalize_expr
from .utils import RuleEngineError, LispExpr


class ConditionalExpr(BaseExpr):
    def __init__(self, *args):
        self.args = list(map(normalize_expr, args))
        types = {arg.get_type() for arg in self.args[1:3]}
        if len(types) != 1:
            raise RuleEngineError("Different return types: {}".format(types))
        self.return_type = types.pop()
        all_fields = reduce(set.union, (arg.all_fields for arg in self.args), set())
        super(ConditionalExpr, self).__init__(all_fields=all_fields)

    def get_type(self):
        return self.return_type
        
    def to_lisp(self):
        args = [arg.to_lisp() for arg in self.args]
        return LispExpr('if', args[0], 'then', args[1], 'else', args[2])
    
    def replace_fields(self, field_map):
        args = [arg.replace_fields(field_map) for arg in self.args]
        return type(self)(*args)
    
    def __str__(self):
        return '({} ? {} : {})'.format(*map(str, self.args))


def if_then_else(condition, then, else_):
    return ConditionalExpr(condition, then, else_)
