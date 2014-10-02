from actions import Assert, Delete, Update
from clips_func import fact_index, gensym, min_, max_
from expr import normalize_expr
from rule import Rule

UNIQUE_INDEX_FIELD = '_uniqueIndex'

class MapReduceFunc(object):
    def _map(self, x): return x
    def _reduce(self, x, y): raise NotImplementedError
    
    def __init__(self, param):
        self.param = param
        self.map_value = self._map(param)

class AssertAggregate(Assert):
    def __init__(self, **kwargs):
        self.map_reduce_values = {}
        for key, value in kwargs.items():
            if isinstance(value, MapReduceFunc):
                kwargs[key] = value.map_value
                self.map_reduce_values[key] = value
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
        reduce_kwargs = {field_name: value._reduce(getattr(r1, field_name), getattr(r2, field_name))
                         for field_name, value in self.map_reduce_values.iteritems()}
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

class Count(Sum):
    def _map(self, x): return 1
