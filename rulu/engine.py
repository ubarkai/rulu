import clips
import os
from def_module_loader import DefModuleLoader
from func import RuleFunc
from utils import RuleEngineError, logger

class RuleEngine(object):
    def __init__(self, trace=False):
        self.environment = clips.Environment()
        self.logger = logger.getChild(type(self).__name__)
        self.clips_types = {}
        self.preprocess_funcs = []
        self.postprocess_funcs = []
        RuleFunc._register_engine(self)
        self.environment.DebugConfig.ActivationsWatched = trace
        
    def load_module(self, module_name, package=None):
        """ 
        Load data model and rule definitions from the given Python module 
        """
        DefModuleLoader(self).load(module_name, package)

    def assert_(self, fact_type, **values):
        """ 
        Assert a new fact 
        """
        fact = fact_type(**values)
        self.environment.Assert(fact._clips_obj)
        
    def run(self):
        self.run_one_cycle()
        
    def run_one_cycle(self, limit_steps=None):
        """
        Run a single cycle of the rule engine
        
        limit_steps: maximal number of execution steps (or None to run 
                     until completion)
        """
        for preprocess_func in self.preprocess_funcs:
            self.logger.info('Calling: %s', preprocess_func)
            preprocess_func()
        RuleFunc._clear_error()
        if limit_steps:
            self.logger.info('Running rule engine (%d steps)', limit_steps)
        else:
            self.logger.info('Running rule engine')
        self.environment.Run(limit_steps)
        self.logger.info('Rule engine completed')
        RuleFunc._check_error()
        for postprocess_func in self.postprocess_funcs:
            self.logger.info('Calling: %s', postprocess_func)
            postprocess_func()
            
    def get_facts(self):
        """
        Return an interator over all known facts
        """
        return (self._wrap_clips_instance(fact) for fact in self.environment.FactList()
                if fact.Relation != 'initial-fact')
    
    def clear(self):
        self.environment.Clear()
        
    def reset(self):
        """
        1. Remove all activated rules from agenda
        2. Remove all facts from the fact-list
        3. Assert the facts from existing deffacts
        """
        self.environment.Reset()
        
    def load(self, filename):
        """
        Load facts and class instances from a text file in CLIPS format
        (as written by the save() method)
        """
        try:
            self.logger.debug('Loading facts from {}'.format(filename))
            self.environment.LoadFacts(filename)
            instance_filename = _get_instance_filename(filename)
            if os.path.exists(instance_filename):
                self.environment.LoadInstances(instance_filename)
        except IOError:
            raise RuleEngineError('Error while loading {}.\n Error log:\n{}'.format(filename, clips.ErrorStream.Read()))
        
    def save(self, filename):
        """
        Save all facts and class instances to a text file in CLIPS format
        """
        self.logger.debug('Saving facts to {}'.format(filename))
        self.environment.SaveFacts(filename)
        
        instance_filename = _get_instance_filename(filename)
        self.logger.debug('Saving instances to {}'.format(instance_filename))
        self.environment.SaveInstances(instance_filename)
        
    def register_clips_type(self, clips_type):
        self.clips_types[clips_type._name] = clips_type
        
    def get_rule_names(self):
        """
        List the names of all the defined rules
        """
        return [str(t).rsplit('::', 1)[1] for t in self.environment.RuleList()]

    def _wrap_clips_instance(self, instance):
        """
        Take a fact/instance as returned from PyCLIPS, and wrap it in the
        appropriate Fact/Class instance.
        """
        if isinstance(instance, clips.InstanceName):
            instance = self.environment.FindInstance(instance)
            return self.clips_types[str(instance.Class)](_clips_obj=instance)
        else:
            return self.clips_types[str(instance.Relation)](_clips_obj=instance)

def _get_instance_filename(fact_filename):
    tokens = fact_filename.rsplit('.', 1)
    tokens[0] += '.instances'
    return '.'.join(tokens)
