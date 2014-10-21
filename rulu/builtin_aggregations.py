from actions import Assert, Delete, Update
from clips_func import fact_index, gensym, min_, max_, create_multifield, concatenate
from conditional_expr import if_then_else
from expr import normalize_expr, BaseExpr
from rule import Rule

UNIQUE_INDEX_FIELD = '_uniqueIndex'

class MapReduceFunc(BaseExpr):
    def _map(self, *x): return x
    def _reduce(self, x, y): raise NotImplementedError
    
    def __init__(self, *params):
        self.params = map(normalize_expr, params)
        all_fields = set().union(*(param.all_fields for param in self.params))
        super(MapReduceFunc, self).__init__(all_fields=all_fields)
        map_values = self._map(*self.params)
        if not isinstance(map_values, (tuple, list)):
            map_values = [map_values]
        self.map_values = map(normalize_expr, map_values)
        
    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, 
                               ', '.join(str(param) for param in self.params))
        
    def __repr__(self):
        return '<{}>'.format(self)
        
    def get_type(self):
        return self.params[0].get_type()

class AssertAggregate(Assert):
    def __init__(self, **kwargs):
        self.map_reduce_values = {}
        for key, value in kwargs.items():
            if isinstance(value, MapReduceFunc):
                del kwargs[key]
                subkeys = []
                for n, map_value in enumerate(value.map_values):
                    subkey = key if n == 0 else '{}_{}'.format(key, n+1)
                    kwargs[subkey] = map_value
                    subkeys.append(subkey)
                self.map_reduce_values[key] = (value, subkeys)
        super(AssertAggregate, self).__init__(**kwargs)
        
    def prepare_rule(self, rule):
        if rule.salience is None:
            rule.salience = -1000
        self.data.update({key : normalize_expr(value) for key, value in rule.groupby.iteritems()})
        self.data[UNIQUE_INDEX_FIELD] = gensym()  
        super(AssertAggregate, self).prepare_rule(rule)
        self._create_reduce_rule(rule)
        
    def _create_reduce_rule(self, map_rule):
        r1 = map_rule.target[0]
        r2 = map_rule.target[1]
        self.reduce_rule = Rule()
        self.reduce_rule.set_name('_Reduce')
        for field_name in map_rule.groupby:
            self.reduce_rule.add_variable(getattr(r1, field_name), getattr(r2, field_name))
        self.reduce_rule.add_condition(fact_index(r1) != fact_index(r2))
        
        reduce_kwargs = {}
        for field_name, (value, subfields) in self.map_reduce_values.iteritems():
            v1 = [getattr(r1, field_name) for field_name in subfields]
            v2 = [getattr(r2, field_name) for field_name in subfields]
            if len(subfields) == 1: 
                v1 = v1[0]
                v2 = v2[0]
            reduced = value._reduce(v1, v2)
            if len(subfields) == 1:
                reduced = [reduced]
            reduce_kwargs.update(dict(zip(subfields, reduced)))
        self.reduce_rule.add_action(Delete(r2))
        self.reduce_rule.add_action(Update(r1, **reduce_kwargs))
        self.reduce_rule.set_salience(map_rule.salience)
        map_rule.add_secondary_rule(self.reduce_rule)
        
class Sum(MapReduceFunc): 
    def _reduce(self, x, y): return x + y

class Max(MapReduceFunc):
    def _reduce(self, x, y): return max_(x, y)
    
class Min(MapReduceFunc):
    def _reduce(self, x, y): return min_(x, y)
    
class Concatenate(MapReduceFunc):
    def _map(self, x):
        return create_multifield(x)
     
    def _reduce(self, x, y):
        return concatenate(x, y)

class BaseArgMinMax(MapReduceFunc):
    def __init__(self, x, key):
        return super(BaseArgMinMax, self).__init__(x, key)
    
    def _reduce(self, x, y):
        condition = self._condition(x[1], y[1]) 
        return (if_then_else(condition, x[0], y[0]), if_then_else(condition, x[1], y[1]))

class ArgMin(BaseArgMinMax):
    def _condition(self, x, y): return x <= y

class ArgMax(BaseArgMinMax):
    def _condition(self, x, y): return x >= y
    
class Count(Sum):
    def _map(self): return 1
    
__all__ = 'AssertAggregate Sum Max Min ArgMax ArgMin Count Concatenate'.split()
