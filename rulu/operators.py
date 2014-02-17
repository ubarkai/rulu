from expr import BaseExpr, VariableExpr, normalize_expr
from typedefs import Boolean, Integer, Number
from utils import LispExpr, RuleEngineError

class BaseBinaryOperator(BaseExpr):
    def __init__(self, lhs, rhs, op):
        super(BaseBinaryOperator, self).__init__(all_fields=lhs.all_fields.union(rhs.all_fields))
        self.lhs = lhs
        self.rhs = rhs
        self.op = op
        
    def to_lisp(self):
        return LispExpr(self.op, self.lhs.to_lisp(), self.rhs.to_lisp())
    
    def replace_fields(self, field_map):
        return type(self)(lhs=self.lhs.replace_fields(field_map), 
                          rhs=self.rhs.replace_fields(field_map),
                          op=self.op)
        
    def __str__(self):
        return '({} {} {})'.format(self.lhs, self.op, self.rhs)
    
class ArithmeticBinaryOperator(BaseBinaryOperator, BaseExpr):
    def get_type(self):
        lhs_type, rhs_type = self.lhs.get_type(), self.rhs.get_type()
        if lhs_type in (Integer, Number) and rhs_type in (Integer, Number):
            return Integer if lhs_type is Integer and rhs_type is Integer else Number
        else:
            raise RuleEngineError('Illegal operator "{}" on {} and {}'.format(
                    self.op.__name__, self.lhs.get_type(), self.rhs.get_type()))
    
class BooleanBinaryOperator(BaseBinaryOperator, BaseExpr):
    def get_type(self):
        return Boolean
    
class Condition(BaseExpr):
    def __init__(self, expr):
        expr = normalize_expr(expr)
        super(Condition, self).__init__(all_fields=expr.all_fields)
        if expr.get_type() is not Boolean:
            raise RuleEngineError('Condition must be of boolean type. Got "{}", which is {}'.format(expr, expr.get_type()))
        self.expr = expr
        
    def get_type(self):
        return Boolean

    def to_lisp(self):
        expr = self.expr
        if isinstance(self.expr, VariableExpr):
            expr = not_(not_(expr))
        return LispExpr('test', expr.to_lisp())
    
    def replace_fields(self, field_map):
        return type(self)(self.expr.replace_fields(field_map))
    
    def __str__(self):
        return 'Condition <{}>'.format(self.expr)
    
class UnaryOperator(BaseExpr):
    def __init__(self, expr, op):
        super(UnaryOperator, self).__init__(all_fields=expr.all_fields)
        self.expr = expr
        self.op = op
        
    def get_type(self):
        return self.expr.get_type()
    
    def to_lisp(self):
        return LispExpr(self.op, self.expr.to_lisp())
    
    def replace_fields(self, field_map):
        return type(self)(expr=self.expr.replace_fields(field_map), 
                          op=self.op)
        
    def __str__(self):
        return '({} {})'.format(self.op, self.expr)

or_ = lambda lhs, rhs: BooleanBinaryOperator(normalize_expr(lhs), normalize_expr(rhs), op='or')
not_ = lambda expr: UnaryOperator(normalize_expr(expr), op='not')
