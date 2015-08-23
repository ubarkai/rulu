import clips
from actions import Update
from slots import HasSlots, SlotsMeta
from expr import BaseExpr, ConvertibleToExpr
from typedefs import FactIndexType
from utils import Printable, wrap_clips_errors

RULU_INTERNAL_PREFIX = '_rulu_internal'

class FactReference(ConvertibleToExpr):
    def _update_python_param(self, params, value):
        raise NotImplementedError
    
    def _from_python_params(self, params):
        raise NotImplementedError

class FactMeta(SlotsMeta, FactReference):
    def __getitem__(self, key):
        return self._indexed_reference(key)
    
indexed_references = {}

class Fact(HasSlots):
    __metaclass__ = FactMeta
    CLIPS_INSTANCE_TYPE = clips.Fact
            
    @classmethod
    @wrap_clips_errors
    def _build(cls, engine):
        if cls is not Fact: 
            super(Fact, cls)._build(engine)
            cls._clips_type = engine.environment.BuildTemplate(cls._name, cls._slots)
        
    @classmethod
    def _to_expr(cls):
        if '_fact_expr' not in cls.__dict__:
            cls._fact_expr = FactExpr(cls)
        return cls._fact_expr

    def _create_clips_obj(self):
        return self._clips_type.BuildFact()

    def _copy_clips_obj(self, obj):
        return obj if hasattr(obj, '_Fact__env') else self._environment.Fact(obj)
    
    def _clips_index(self):
        return self._clips_obj.Index
    
    def _delete(self):
        self._clips_obj.Retract()
        
    def _update(self, **kwargs):
        cmd = Update(self._clips_obj.Index, **kwargs).to_lisp()
        self._environment.SendCommand(str(cmd))
        
    @classmethod
    def _update_python_param(cls, params, value):
        params[cls._name] = value
        
    @classmethod
    def _from_python_params(cls, params):
        return params[cls._name]

    @classmethod
    def _indexed_reference(cls, index):
        return indexed_references.setdefault((cls, index), IndexedFactReference(cls, index))

class IndexedFactReference(Printable, FactReference):
    def __init__(self, template_cls, key):
        self._template_cls = template_cls
        self._key = key
        self._fields = {}
        self._fact_expr = FactExpr(self)
        for key, field in template_cls._fields.iteritems():
            new_field = type(field)(_type=field.get_type())
            new_field._init(self, key)
            self._fields[key] = new_field
            setattr(self, key, new_field)

    def _to_expr(self):
        return self._fact_expr

    def __str__(self):
        return '{}[{}]'.format(self._template_cls._name, repr(self._key))
    
    def _update_python_param(self, params, value):
        params.setdefault(self._template_cls._name, {})[self._key] = value
    
    def _from_python_params(self, params):
        return params[self._name][self._key]

    @property
    def _name(self):
        return self._template_cls._name
    
class FactExpr(BaseExpr):
    def __init__(self, fact):
        super(FactExpr, self).__init__(all_fields=[self])
        self.fact = fact
        
    def __str__(self):
        return str(self.fact)
    
    def get_type(self):
        return FactIndexType

    def to_lisp(self):
        return str(self)
