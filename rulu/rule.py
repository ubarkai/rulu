from collections import defaultdict
from functools import partial

from actions import Assert
from expr import FieldExpr, VariableExpr, IntegerField
from fact import Fact, FactExpr, RULU_INTERNAL_PREFIX
from func import RuleFunc
from operators import Condition
from slots import make_slotted_type
from typedefs import TYPE_MAP, FactIndexType, Integer
from utils import LispExpr, RuleEngineError, UniqueIdCounter, logger, wrap_clips_errors

class RulePremise(object):
    def __init__(self, container, var_name):
        self.container = container
        self.var_name = var_name
        self.negative = False
        self.field_values = set() # (field, value) pairs
        
    def add(self, field, value):
        assert field.container is self.container, (field.container, self.container)
        self.field_values.add((field, value))
        
    def set_negative(self):
        self.negative = True
        
    def build_lisp(self):
        field_values = sorted(self.field_values, key = lambda (field, value) : str(field))
        res = LispExpr(self.container._name, *(LispExpr(field.name, value) for field, value in field_values))
        if self.negative:
            res = LispExpr('not', res)
        return res
        
    def build_str(self, with_varname=True):
        res = str(self.build_lisp())
        if not res.startswith('('):
            res = '({})'.format(res)
        if with_varname and not self.negative:
            res = '{} <- {}'.format(self.var_name, res)
        return res
        
    def build_target_field(self):
        return LispExpr(self.target_field_name, self.target_field_var)
        
class Rule(object):
    def __init__(self):
        self.premises = defaultdict(RulePremise)
        self.name = None
        self.description = None
        self.target = None
        self.target_fields = None
        self.salience = None
        self.variable_map = {}
        self.conditions = []
        self.actions = []
        self.python_actions = []
        self.aggregator_classes = []
        self.groupby = {}
        self.secondary_rules = []
        self.num_functions = 0
        self.comments = None
        
        self.premise_varnames = UniqueIdCounter('?fact')
        self.general_varnames = UniqueIdCounter('?var')
        
    def set_target(self, target=None):
        if self.target_fields is not None:
            raise RuleEngineError('Cannot set both target template and target fields')
        self.target = target
        self.target_fields = target._fields
        
    def set_name(self, name):
        if self.name not in (None, name):
            raise RuleEngineError('Tried to set target name to "{}", but it is already "{}"'.format(name, self.name))
        self.name = name
            
    def set_description(self, description):
        self.description = description
        
    def set_target_fields(self, **fields):
        if self.target is not None:
            raise RuleEngineError('Target already set')
        self.target_fields = {key: FieldExpr(_type=TYPE_MAP.get(_type, _type)) for key, _type in fields.iteritems()}
        self.target = make_slotted_type(Fact, self.name, **self.target_fields)
        
    def get_target_fields(self):
        return self.target_fields
    
    def get_target_name(self):
        if self.target is not None and self.target._name is not None:
            return self.target._name
        else:
            return self.name
        
    def set_salience(self, salience):
        self.salience = salience
        
    def add_variable(self, *fields):
        matching_var_names = set()
        for field in sorted(fields, key=str):
            if not isinstance(field, (FieldExpr, FactExpr)):
                raise TypeError('Exepected field or fact, found {}'.format(field))
            try:
                matching_var_names.add(self.variable_map[field].var_name)
            except KeyError:
                pass
        
        if not matching_var_names:
            var_name = self.general_varnames.next()
        else:
            var_names = sorted(matching_var_names)
            var_name = var_names[0]
            for prev_var_name in var_names[1:]:
                self._replace_variable(prev_var_name, var_name)

        for field in fields:
            if isinstance(field, FactExpr):
                self.set_premise(field.fact)
            else:
                self.set_premise(field.container).add(field, var_name)
                self.variable_map[field] = VariableExpr(var_name, field.get_type())
        return var_name
    
    def add_condition(self, expr):
        condition = Condition(expr)
        for field in condition.all_fields:
            self.add_variable(field)
        self.conditions.append(condition)

    def add_action(self, action):
        for field in action.get_all_fields():
            self.add_variable(field)
        action.prepare_rule(self)
        self.actions.append(action)
                
    def add_python_action(self, function):
        self.python_actions.append(function)
        
    def add_aggregator_cls(self, aggregator_cls):
        self.aggregator_classes.append(aggregator_cls)
        
    def set_comments(self, comments):
        self.comments = comments

    def set_premise(self, container):
        premise = self.premises.get(container)
        if premise is None:
            var_name = self.premise_varnames.next()
            premise = RulePremise(container, var_name)
            self.premises[container] = premise
            self.variable_map[container._to_expr()] = VariableExpr(var_name, FactIndexType)
        return premise

    def set_negative_premise(self, container):
        self.set_premise(container).set_negative()
        
    def set_groupby(self, **kwargs):
        self.groupby.update(kwargs)
        
    def add_secondary_rule(self, rule):
        self.secondary_rules.append(rule)
            
    def _replace_variable(self, prev_var_name, var_name):
        # TODO: Implement this
        raise NotImplementedError()

    @wrap_clips_errors
    def build(self, engine):
        if self.target is not None:
            self._init_target(engine)
        self._init_aggregators(engine)
        if self.python_actions:
            target_name = self.target._name if self.target else None
            self._add_python_action(engine, target_name)
        lhs = str(self._build_lhs())
        rhs = str(self._build_rhs())
        if self.name is None:
            self.name = '_anonymous_rule'
        rule_num = sum(1 for rule_name in engine.get_rule_names() if rule_name.startswith(self.name+'@'))
        self.clips_name = '{}@{}'.format(self.name, rule_num+1)
        logger.getChild('rule').debug('Creating rule: %s\n<%s\n%s\n%s>\n%s', 
                self.clips_name, '='*20, lhs, '='*20, rhs)
        self.clips_rule = engine.environment.BuildRule(self.clips_name, lhs, rhs, self.comments)
        for secondary_rule in self.secondary_rules:
            secondary_rule.build(engine)

    def _init_target(self, engine):
        target_name = self.get_target_name()
        if target_name is None:
            raise RuleEngineError('Cannot build rule, target name not set or multiple targets have the same name')
        if self.name is None:
            self.name = target_name
        if self.target._name is None:
            self.target._name = target_name
        if target_name not in engine.clips_types:
            self.target._build(engine)
        
    def _init_aggregators(self, engine):
        # TODO: Move this to separate module with secondary rule
        for aggregator_cls in self.aggregator_classes:
            aggregator = aggregator_cls(engine=engine, template=self.target)
            engine.preprocess_funcs.append(aggregator.init)
            self.add_python_action(lambda assert_, **kwargs : aggregator.process_one(**kwargs))
            finalize_name = '{}_{}_finalize'.format(RULU_INTERNAL_PREFIX, self.name)
            finalize_fact_cls = type(Fact)(finalize_name, (Fact, ), {'x': IntegerField()})
            finalize_fact_cls._build(engine)
            target = self.target
            self.target = finalize_fact_cls
            if self.salience is None: self.salience = -1000
            self.add_action(Assert(x=0))
            finalize_rule = Rule()
            finalize_rule.set_name(finalize_name)
            finalize_rule.set_premise(finalize_fact_cls)
            finalize_rule.set_salience(self.salience)
            finalize_rule.set_target(target)
            self.set_salience((self.salience)+1)
            finalize_rule.add_python_action(lambda assert_, **kwargs: aggregator.finalize(assert_))
            finalize_rule.build(engine)
            
    def _add_python_action(self, engine, target_name):
        func = RuleFunc(partial(self._action, engine), Integer, 'target_{}'.format(target_name))
        params = [premise.container for premise in self.premises.itervalues()]
        self.actions.append(func(*params).replace_fields(self.variable_map))
        
    def _build_lhs(self):
        lhs = []
        if self.salience is not None:
            lhs.append(LispExpr('declare', LispExpr('salience', self.salience)))
        lhs.extend(premise.build_str() for premise in sorted(self.premises.itervalues(), key=lambda p:p.var_name))
        lhs.extend(condition.replace_fields(self.variable_map).to_lisp() for condition in self.conditions) 
        return '\n'.join(str(x) for x in lhs)
    
    def _build_rhs(self):
        return '\n'.join(str(action.replace_fields(self.variable_map).to_lisp()) for action in self.actions)
    
    def _make_field_map(self):
        return {}
    
    def _action(self, _engine, *facts):
        params = {}
        for var, fact in zip(self.premises, facts):
            var._update_python_param(params, fact)
        if self.target is not None:
            params['assert_'] = lambda **kwargs : _engine.assert_(self.target, **kwargs)
        for func in self.python_actions:
            func(**params)
