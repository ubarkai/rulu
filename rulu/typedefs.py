"""
This module defines the possible types in the rule engine, and provides 
conversions from and to Python types.
"""

from calendar import timegm
from collections.abc import Iterable
from datetime import datetime
import clips


class RuleEngineType(object):
    """
    Base class for a possible type
    """
    PYTHON_TYPE = None
    PYTHON_TYPE_CHECK = None
    CLIPS_TYPE = None
    DEFAULT = None

    @classmethod
    def _isinstance(cls, x):
        """ Check if argument is of the current type """
        return isinstance(x, cls.PYTHON_TYPE_CHECK)
    
    @classmethod
    def _from_clips_value(cls, x):
        """ Convert from CLIPS value to Python value """
        return cls.DEFAULT if x is None else cls.PYTHON_TYPE(x)
    
    @classmethod
    def _to_clips_value(cls, x):
        """ Convert from Python value to CLIPS value """
        return x


class Integer(RuleEngineType):
    PYTHON_TYPE = int
    PYTHON_TYPE_CHECK = int
    CLIPS_TYPE = 'INTEGER'
    DEFAULT = 0


class Boolean(Integer):
    PYTHON_TYPE = bool
    PYTHON_TYPE_CHECK = bool
    CLIPS_TYPE = 'SYMBOL'
    TRUE = clips.Symbol('TRUE')
    FALSE = clips.Symbol('FALSE')
    DEFAULT = FALSE

    @classmethod
    def _to_clips_value(cls, x):
        if isinstance(x, clips.Symbol):
            return x
        elif x:
            return cls.TRUE
        else:
            return cls.FALSE
    
    @classmethod
    def _from_clips_value(cls, x):
        return str(x) == 'TRUE'


class Number(RuleEngineType):
    PYTHON_TYPE = float
    PYTHON_TYPE_CHECK = (int, float)
    CLIPS_TYPE = 'NUMBER'
    DEFAULT = 0.0


class String(RuleEngineType):
    PYTHON_TYPE = str
    PYTHON_TYPE_CHECK = str
    CLIPS_TYPE = 'STRING'
    DEFAULT = ''


class Unicode(String):
    pass


class Symbol(String):
    CLIPS_TYPE = 'SYMBOL'
    DEFAULT = ''


class DateTime(RuleEngineType):
    """
    Date-time object. 
    There is no date object in CLIPS, we use an integer representation to
    allow for comparisons and arithmetic.
    """
    PYTHON_TYPE = datetime
    PYTHON_TYPE_CHECK = datetime
    CLIPS_TYPE = 'INTEGER'
    DEFAULT = datetime.fromtimestamp(0)
    
    @classmethod
    def _to_clips_value(cls, x):
        return timegm(x.utctimetuple())

    @classmethod
    def _from_clips_value(cls, x):
        return datetime.utcfromtimestamp(x)
    

class Multifield(RuleEngineType):
    """
    Multifield type. Maps to Python list.
    """
    PYTHON_TYPE = list
    PYTHON_TYPE_CHECK = Iterable
    CLIPS_TYPE = 'MULTIFIELD'
    DEFAULT = ()
     

class FactIndexType(RuleEngineType): pass


TYPE_MAP = {t.PYTHON_TYPE: t for t in (Integer, Number, String, Boolean, DateTime)}
