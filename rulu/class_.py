"""
Basic wrapper for CLIPS Object-Oriented (COOL) constructs 
"""

import clips
from expr import FieldExpr, BaseExpr
from slots import HasSlots
from typedefs import RuleEngineType
from utils import wrap_clips_errors

class Class(HasSlots, RuleEngineType):
    CLIPS_INSTANCE_TYPE = clips.Instance
    CLIPS_TYPE = 'INSTANCE'
            
    @classmethod
    @wrap_clips_errors
    def _build(cls, engine):
        if cls is not Class:
            super(Class, cls)._build(engine)
            definition = '(is-a USER){}'.format(cls._slots)
            cls._clips_type = engine.environment.BuildClass(cls._name, definition)
        
    def _create_clips_obj(self):
        return self._clips_type.BuildInstance()

    def _copy_clips_obj(self, obj):
        return obj if hasattr(obj, '_Instance__env') else self._environment.Instance(obj)
    
    @classmethod
    def _from_clips_value(cls, x):
        if isinstance(x, clips.InstanceName):
            return cls(_clips_obj=cls._environment.FindInstance(x))
        else: # Instance
            return cls(_clips_obj=x)
    
    @classmethod
    def _isinstance(cls, x):
        return isinstance(x, cls)
    
class InstanceField(FieldExpr):
    def __init__(self, _type):
        super(InstanceField, self).__init__(_type)
        for key, field in _type._fields.iteritems():
            setattr(self, key, InstanceMember(self, key, field))
            
class InstanceMember(BaseExpr):
    def __init__(self, container, key, field):
        super(InstanceMember, self).__init__(all_fields=[container])
        self._container = container
        self._key = key
        self._field = field
        
    def __str__(self):
        return '{}.{}'.format(self._container, self._key)
    
    def get_type(self):
        return self._field._type

    def to_lisp(self):
        return '(send {} get-{})'.format(self._container.to_lisp(), self._key)

    def replace_fields(self, field_map):
        return InstanceMember(self._container.replace_fields(field_map), self._key, self._field)
