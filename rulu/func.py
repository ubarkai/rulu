"""
This module provides the mechanism for wrapping user-defined Python functions
so that they can be called inside rules (in conditions, assertions etc.)
"""

import clips
import functools
import sys
from .clips_func import PythonFuncExpr
from .typedefs import Boolean, String, Integer, Number
from .utils import UniqueIdCounter, logger


class RuleFunc(object):
    """
    Wrap a Python function to be usable inside the rule engine
    """
    _last_error = None
    _counters = {}
    _engine_by_environment = {}
    _cur_engine = None
    NUM_CALLS_PER_PRINT = 1000
    
    def __init__(self, func, return_type=String, func_name=None):
        self.func = func
        self.type = return_type
        self.func_name = func_name or func.__name__
        self._wrapper_by_engine = {}
        self._num_calls = 0
        
    def __call__(self, *args, **kwargs):
        """
        Return an expression that indicates an invocation of this function with
        given arguments.
        """
        wrapper = self._wrapper_by_engine.get(self._cur_engine)
        if wrapper is None:
            wrapper = self._create_wrapper(self._cur_engine)
            self._cur_engine.environment.define_function(wrapper)
        return PythonFuncExpr(wrapper.__name__, self.type, *args)
    
    def _create_wrapper(self, engine):
        """
        Creates a wrapper Python function that would be run by PyCLIPS.
        It calls the user defined function and is also responsible for handling
        errors and for type conversions.
        """
        def wrapper(*args):
            if self._last_error is not None:
                return
            try:
                args = [(engine._wrap_clips_instance(arg) if isinstance(arg, 
                    (clips.TemplateFact, clips.InstanceName)) else arg) for arg in args]
                res = self.func(*args)
                self._num_calls += 1
                if self._num_calls % self.NUM_CALLS_PER_PRINT == 0:
                    logger.debug('{}: called {} times.'.format(self.func_name, self._num_calls))
                return self.type._to_clips_value(res)
            except:
                # Register error to be raised later by engine
                cls = type(self)
                type(self)._last_error = sys.exc_info()
                # Abort CLIPS execution
                engine.environment.Clear()
        wrapper.__name__ = self._counters.setdefault(self.func_name, UniqueIdCounter(self.func_name+'_')).next()
        return wrapper
    
    # Global methods for internal use

    @classmethod
    def _register_engine(cls, engine):
        cls._engine_by_environment[engine.environment] = engine
        
    @classmethod
    def _set_cur_engine(cls, engine):
        cls._cur_engine = engine
            
    @classmethod    
    def _clear_error(cls):
        cls._last_error = None
        
    @classmethod
    def _check_error(cls):
        if cls._last_error:
            raise cls._last_error[0](cls._last_error[1]).with_traceback(cls._last_error[2])

TypedRuleFunc = lambda return_type : functools.partial(RuleFunc, return_type=return_type)

# Shortcuts for defining functions with different return types
BooleanRuleFunc = TypedRuleFunc(Boolean)
IntegerRuleFunc = TypedRuleFunc(Integer)
NumberRuleFunc = TypedRuleFunc(Number)
StringRuleFunc = TypedRuleFunc(String)
