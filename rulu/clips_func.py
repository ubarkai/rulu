import clips
from .expr import BaseExpr, normalize_expr, SymbolExpr
from .typedefs import Integer, Number, String, Symbol, FactIndexType, Boolean, Multifield
from .utils import LispExpr
from functools import reduce


class ClipsFuncExpr(BaseExpr):
    def __init__(self, func_name, return_type, *args):
        self.func_name = func_name
        self.return_type = return_type
        self.args = [normalize_expr(arg) for arg in args]
        all_fields = reduce(set.union, (arg.all_fields for arg in self.args), set())
        super().__init__(all_fields=all_fields)
        
    def get_type(self):
        return self.return_type
        
    def to_lisp(self):
        if not self.args:
            return '({})'.format(self.func_name)
        else:
            return LispExpr(self.func_name, *(arg.to_lisp() for arg in self.args))
    
    def replace_fields(self, field_map):
        args = [arg.replace_fields(field_map) for arg in self.args]
        return self._duplicate_with_args(*args)

    def evaluate(self):
        return clips.Eval(str(self.to_lisp())).encode()
    
    def _duplicate_with_args(self, *args):
        return ClipsFuncExpr(self.func_name, self.return_type, *args)
    
    def __str__(self):
        return '{}({})'.format(self.func_name, ','.join(map(str, self.args)))


class ConcatenateExpr(ClipsFuncExpr):
    def __init__(self, *args):
        super().__init__('', Multifield, *args)
    
    def _duplicate_with_args(self, *args):
        return ConcatenateExpr(*args)
        
    def to_lisp(self):
        return ' '.join(str(arg.to_lisp()) for arg in self.args)
     

class PythonFuncExpr(ClipsFuncExpr):
    def __init__(self, python_func_name, return_type, *args):
        super().__init__(SymbolExpr(python_func_name), return_type, *args)
        
    def to_lisp(self):
        if self.return_type is Boolean:
            return (self != 0).to_lisp()
        else:
            return super(PythonFuncExpr, self).to_lisp()


def clips_func(funcname, return_type):
    def func(*args):
        return ClipsFuncExpr(funcname.replace('_', '-'), return_type, *args)
    func.__name__ = funcname
    return func


# TODO: Add more functions
min_ = clips_func('min', Number)
max_ = clips_func('max', Number)
fact_index = clips_func('fact-index', FactIndexType)
gensym = clips_func('gensym', Symbol)
create_multifield = clips_func('create$', Multifield)
insert_multifield = clips_func('insert$', Multifield)
length_multifield = clips_func('length$', Integer)


def concatenate(*args):
    return ConcatenateExpr(*args)
