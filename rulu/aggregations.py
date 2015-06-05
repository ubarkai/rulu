"""
This module implements aggregators, in which facts are collected during 
the rule engine execution and then aggregated in Python code afterwards. 
"""


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
        """ Runs before rule engine execution """
        pass
    
    def finalize(self, assert_):
        """ Runs after rule engine execution """
        self.finalized = True
    
    def process_one(self, **kwargs):
        """ Runs on each fact to be aggregated """
        raise NotImplementedError

def grouping_aggregator(keys, func):
    """ 
    'Groupby' aggregator. Facts are collected to lists grouped by
    (zero or more) keys and then each group is processed separately
    by the given 'func'
    """ 
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
