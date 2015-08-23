from utils import Printable, RuleEngineError
from typedefs import Boolean, DateTime, Integer, Number, String, Unicode, Symbol

class BaseExpr(Printable):
    def __init__(self, all_fields=[]):
        self.all_fields = set(all_fields)
        
    def to_lisp(self): raise NotImplementedError
    def evaluate(self): raise NotImplementedError

    def __gt__(self, rhs): return self._boolean_operator(rhs, '>')
    def __ge__(self, rhs): return self._boolean_operator(rhs, '>=')
    def __lt__(self, rhs): return self._boolean_operator(rhs, '<')
    def __le__(self, rhs): return self._boolean_operator(rhs, '<=')
    def __eq__(self, rhs): return self._boolean_operator(rhs, 'eq')
    def __ne__(self, rhs): return self._boolean_operator(rhs, 'neq')
    
    def __add__(self, rhs): return self._binary_operator(rhs, '+')
    def __sub__(self, rhs): return self._binary_operator(rhs, '-')
    def __mul__(self, rhs): return self._binary_operator(rhs, '*')
    def __div__(self, rhs): return self._binary_operator(rhs, '/')
    def __pow__(self, rhs): return self._binary_operator(rhs, '**')
    
    def _binary_operator(self, rhs, op):
        from operators import ArithmeticBinaryOperator
        return ArithmeticBinaryOperator(op, self, normalize_expr(rhs))
    
    def _boolean_operator(self, rhs, op):
        from operators import BooleanBinaryOperator
        return BooleanBinaryOperator(op, self, normalize_expr(rhs))
    
    def replace_fields(self, field_map):
        return field_map.get(self, self)
    
    def get_type(self):
        raise RuleEngineError('Cannot infer type for {}'.format(self))
    
class PrimitiveExpr(BaseExpr):
    def __init__(self, value):
        super(PrimitiveExpr, self).__init__()
        self.original_value = value
        if isinstance(value, bool): 
            self._type = Boolean
            value = Boolean._to_clips_value(value)
        elif isinstance(value, (int, long)): self._type = Integer
        elif isinstance(value, float): self._type = Number
        elif isinstance(value, str): 
            self._type = String
            value = '"{}"'.format(value.replace('"', '\\"'))
        elif isinstance(value, unicode):
            self._type = Unicode
            value = u'"{}"'.format(value.replace(u'"', u'\\"'))
        else:
            raise TypeError(value)
        self.value = value
        
    def __str__(self):
        return repr(self.value)
    
    def to_lisp(self):
        return self.value
    
    def get_type(self):
        return self._type
    
    def evaluate(self):
        return self.original_value
    
class SymbolExpr(BaseExpr):
    def __init__(self, value, type=None):
        super(SymbolExpr, self).__init__()
        self.value = value
        self.type = type
        
    def to_lisp(self):
        return self.value
    
    def __str__(self):
        return self.value
    
    def get_type(self):
        return self.type
    
class FieldExpr(BaseExpr):
    global_order = 0
    
    def __init__(self, _type=None):
        if _type is not None: self._type = _type
        super(FieldExpr, self).__init__(all_fields=[self])
        self.initialized = False
        self.order = FieldExpr.global_order
        FieldExpr.global_order += 1 
        
    def _init(self, container, field_name):
        self.container = container
        self.name = field_name
        self.initialized = True
        
    def __str__(self):
        if self.initialized:
            return '{}.{}'.format(self.container, self.name)
        else:
            return 'uninitialized'

    def get_type(self):
        return self._type
    
class IntegerField(FieldExpr): _type = Integer
class NumberField(FieldExpr): _type = Number
class StringField(FieldExpr): _type = String
class SymbolField(FieldExpr): _type = Symbol
class UnicodeField(FieldExpr): _type = Unicode
class BooleanField(FieldExpr): _type = Boolean
class DateTimeField(FieldExpr): _type = DateTime

class VariableExpr(BaseExpr):
    def __init__(self, var_name, var_type):
        super(VariableExpr, self).__init__()
        self.var_name = var_name
        self.var_type = var_type
        
    def __str__(self):
        return self.var_name
    
    def to_lisp(self):
        return str(self)
    
    def get_type(self):
        return self.var_type
    
class ConvertibleToExpr(object):
    def _to_expr(self):
        raise NotImplementedError
    
def normalize_expr(expr):
    if isinstance(expr, BaseExpr):
        return expr
    elif isinstance(expr, ConvertibleToExpr):
        return expr._to_expr()
    else:
        try:
            return PrimitiveExpr(expr)
        except TypeError:
            raise RuleEngineError('Expected primitive or expression, found {}'.format(expr))

TRUE = SymbolExpr('TRUE', type=Boolean)
FALSE = SymbolExpr('FALSE', type=Boolean)
UNKNOWN_BOOL = SymbolExpr('UNKNOWN', type=Boolean)
