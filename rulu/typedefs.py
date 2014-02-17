"""
This module defines the possible types in the rule engine, and provides 
conversions from and to Python types.
"""

from calendar import timegm
from datetime import datetime
import clips

class RuleEngineType(object):
    """
    Base class for a possible type
    """
    PYTHON_TYPE = None
    PYTHON_TYPE_CHECK = None
    CLIPS_TYPE = None
    
    @classmethod
    def _isinstance(cls, x):
        """ Check if argument is of the current type """
        return isinstance(x, cls.PYTHON_TYPE_CHECK)
    
    @classmethod
    def _from_clips_value(cls, x):
        """ Convert from CLIPS value to Python value """
        return cls.PYTHON_TYPE(x)
    
    @classmethod
    def _to_clips_value(cls, x):
        """ Convert from Python value to CLIPS value """
        return x

class Integer(RuleEngineType):
    PYTHON_TYPE = int
    PYTHON_TYPE_CHECK = int
    CLIPS_TYPE = 'INTEGER'
    
class Boolean(Integer):
    PYTHON_TYPE = bool
    PYTHON_TYPE_CHECK = bool
    CLIPS_TYPE = 'SYMBOL'
    TRUE = clips.Symbol('TRUE')
    FALSE = clips.Symbol('FALSE')
    
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
    
class String(RuleEngineType):
    PYTHON_TYPE = str
    PYTHON_TYPE_CHECK = basestring
    CLIPS_TYPE = 'STRING'
    
class Unicode(RuleEngineType):
    """
    Unicode string.
    PyCLIPS does not support Unicode values, so we take of the encoding/decoding here 
    """
    ENCODING = 'utf8'
    PYTHON_TYPE = unicode
    PYTHON_TYPE_CHECK = basestring
    CLIPS_TYPE = 'STRING'
    
    @classmethod
    def _to_clips_value(cls, x):
        return x.encode(cls.ENCODING)

    @classmethod
    def _from_clips_value(cls, x):
        return x.decode(cls.ENCODING)
    
class DateTime(RuleEngineType):
    """
    Date-time object. 
    There is no date object in CLIPS, we use an integer representation to
    allow for comparisons and arithmetic.
    """
    PYTHON_TYPE = datetime
    PYTHON_TYPE_CHECK = datetime
    CLIPS_TYPE = 'INTEGER'
    
    @classmethod
    def _to_clips_value(cls, x):
        return timegm(x.utctimetuple())

    @classmethod
    def _from_clips_value(cls, x):
        return datetime.utcfromtimestamp(x)
    
class FactIndexType(RuleEngineType): pass

TYPE_MAP = {t.PYTHON_TYPE: t for t in (Integer, Number, String, Boolean, DateTime)}
