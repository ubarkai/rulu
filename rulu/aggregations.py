from bunch import Bunch
from collections import defaultdict

from expr import FieldExpr
from fact import FactReference
from utils import RuleEngineError

class Aggregator(object):
    def __init__(self, engine, template):
        self.engine = engine
        self.template = template
        self.finalized = False
        
    def init(self):
        pass
    
    def finalize(self, assert_):
        self.finalized = True
    
    def process_one(self, **kwargs):
        raise NotImplementedError

def grouping_aggregator(keys, func):
    keys = tuple(_make_key(key) for key in keys)
    class GroupAggregator(Aggregator):
        def init(self): 
            self.data = defaultdict(lambda : [])
            
        def process_one(self, **kwargs):
            if self.finalized:
                raise RuleEngineError('Aggregation failed')
            key = tuple(key(**kwargs) for key in keys)
            value = kwargs.values()[0] if len(kwargs) == 1 else Bunch(kwargs)
            self.data[key].append(value)
            
        def finalize(self, assert_):
            super(GroupAggregator, self).finalize(assert_)
            for key, group in self.data.iteritems():
                func(group, assert_, *key)
        
    return GroupAggregator

def _make_key(key):
    if isinstance(key, FieldExpr):
        return lambda **kwargs : getattr(_make_key(key.container)(**kwargs), key.name)
    elif isinstance(key, FactReference):
        return lambda **kwargs : key._from_python_params(kwargs)
    else:
        raise TypeError('Invalid group key: {}'.format(type(key)))
