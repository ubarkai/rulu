from .expr import FieldExpr
from .utils import logger, wrap_clips_errors, RuleEngineError
from .typedefs import Multifield

ANONYMOUS = 'Anonymous'


class SlotsMeta(type):
    def __new__(meta, name, bases, attrs): #@NoSelf
        attrs['_fields'] = {k: v for k, v in attrs.items() if isinstance(v, FieldExpr)}
        for base in bases:
            if isinstance(base, meta):
                attrs['_fields'].update(base._fields)
        attrs['_name'] = None if name == ANONYMOUS else name
        attrs['__slots__'] = ('_clips_obj', '_data')
        cls = super(SlotsMeta, meta).__new__(meta, name, bases, attrs)
        cls._instrument()
        return cls

    def __repr__(self):
        return '<{}>'.format(self._name or ANONYMOUS)


class HasSlots(object, metaclass=SlotsMeta):
    _all_subclasses = []

    @classmethod
    def _instrument(cls):
        for key, value in cls._fields.items():
            value._init(container=cls, field_name=key)
        cls._slots = ' '.join(cls._make_slot(key, value._type)
                              for key, value in cls._fields.items())
        cls._clips_type = None # To be filled in _build()
        cls._all_subclasses.append(cls)
        cls._ordered_fields = sorted(cls._fields, key=lambda field : cls._fields[field].order)
        cls._field_order = {name: n for n, name in enumerate(cls._ordered_fields)}

    @classmethod
    def _make_slot(cls, name, type):
        if issubclass(type, Multifield):
            return '(multislot {})'.format(name)
        else:
            return '(slot {} (type {}))'.format(name, type.CLIPS_TYPE)

    @classmethod
    def _build(cls, engine):
        if not cls._fields:
            raise RuleEngineError('{} has no fields'.format(cls._name))
        logger.getChild('slots').debug('Building: %s, slots: %s', cls._name, cls._slots)
        cls._environment = engine.environment
        engine.register_clips_type(cls)

    @classmethod
    def _indexed_reference(self, index):
        raise NotImplementedError

    @wrap_clips_errors
    def __init__(self, **kwargs):
        if self._clips_type is None:
            raise RuleEngineError('Class {} is not bound to a rule engine and cannot be instantiated'.format(type(self)))
        existing_clips_obj = kwargs.get('_clips_obj')
        if existing_clips_obj is None:
            self._clips_obj = self._init_values(**kwargs)
        else:
            self._clips_obj = self._copy_clips_obj(existing_clips_obj)
        self._data = self._init_data()

    def _init_values(self, **kwargs):
        clips_obj = self._create_clips_obj()
        # clips_obj.AssignSlotDefaults()
        for key, value in kwargs.items():
            field = self._fields.get(key)
            if field is None:
                raise RuleEngineError('Field {} does not exist in {}'.format(key, self._name))
            if not field.get_type()._isinstance(value):
                raise RuleEngineError('In {}: expected {} should be of type {}, got {}.'.
                                      format(self._name, key, field.get_type(), value))
            if isinstance(value, HasSlots):
                value = value._clips_obj
            clips_obj[key] = field._type._to_clips_value(value)
        return clips_obj

    def _init_data(self):
        return tuple(self._fields[key]._from_clips_value(self._clips_obj) for key in self._ordered_fields)

    def _create_clips_obj(self):
        raise NotImplementedError
    
    def _copy_clips_obj(self, existing_clips_obj):
        raise NotImplementedError
    
    def __getattribute__(self, key):
        if key != '_fields' and key in self._fields:
            return self._data[self._field_order[key]]
        else:
            return object.__getattribute__(self, key)

    def _as_dict(self):
        return {key : getattr(self, key) for key in self._fields}
    
    def __repr__(self):
        return '<{}: {}>'.format(self._name, self._as_dict())
    

def make_slotted_type(cls, name=None, **fields):
    return SlotsMeta(name or ANONYMOUS, (cls, ), dict(fields))
    
