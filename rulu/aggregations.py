from bunch import Bunch
from collections import defaultdict

from expr import FieldExpr
from fact import FactReference

class Aggregator(object):
    def __init__(self, engine, template):
        self.engine = engine
        self.template = template
        
    def init(self):
        pass
    
    def finalize(self):
        pass
    
    def process_one(self, **kwargs):
        raise NotImplementedError

    def assert_(self, **kwargs):
        self.engine.assert_(self.template, **kwargs)

def groupby(keys, func):
    keys = tuple(_make_key(key) for key in keys)
    class GroupAggregator(Aggregator):
        def init(self): 
            self.data = defaultdict(lambda : [])
            
        def process_one(self, **kwargs):
            key = tuple(key(**kwargs) for key in keys)
            value = kwargs.values()[0] if len(kwargs) == 1 else Bunch(kwargs)
            self.data[key].append(value)
            
        def finalize(self): 
            for key, group in self.data.iteritems():
                func(group, self.assert_, *key)
        
    return GroupAggregator

def _make_key(key):
    if isinstance(key, FieldExpr):
        return lambda **kwargs : getattr(_make_key(key.container)(**kwargs), key.name)
    elif isinstance(key, FactReference):
        return lambda **kwargs : key._from_python_params(kwargs)
    else:
        raise TypeError('Invalid group key: {}'.format(type(key)))
