"""
General utility classes and constructs.
"""

import clips
import functools
import logging
import sys

class RuleEngineError(Exception): pass

def wrap_clips_errors(func):
    """
    Add error details (from CLIPS error stream) to CLIPS exceptions. 
    """
    @functools.wraps(func)
    def new_func(*a, **kw):
        try:
            return func(*a, **kw)
        except clips.ClipsError:
            raise RuleEngineError(clips.ErrorStream.Read()), None, sys.exc_info()[2]
    return new_func

class Printable(object):
    """ 
    Add type name to CLIPS object representation.
    """
    def __str__(self):
        raise NotImplementedError
    
    def __repr__(self):
        return '<{} ({})>'.format(type(self).__name__, self) 

class LispExpr(object):
    """
    Represents a nested LISP-like expression.
    """
    def __init__(self, *values):
        if len(values) == 1:
            self.values = values
        else:
            self.values = []
            for v in values:
                if isinstance(v, tuple): v = LispExpr(*v)
                elif not isinstance(v, LispExpr): v = LispExpr(v)
                self.values.append(v)
        
    def __str__(self):
        """
        Return current expression in LISP format.
        """
        res = ' '.join(str(v) for v in self.values)
        if len(self.values) > 1:
            res = '({})'.format(res)
        return res

    def __repr__(self):
        return '<{} ({})>'.format(type(self), self) 

class UniqueIdCounter(object):
    def __init__(self, prefix):
        self.prefix = prefix
        self.count = 0
        
    def next(self):
        self.count += 1
        return '{}{}'.format(self.prefix, self.count)

logger = logging.getLogger('ruleengine')
