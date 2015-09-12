from bisect import bisect
from collections import defaultdict
from itertools import product


class FactNotFoundError(Exception): pass


class Trace(object):
    def __init__(self, fact, rule=None, src_traces=[]):
        self.fact = fact
        self.rule = rule
        self.src_traces = src_traces
        
        self.all_facts = {fact}
        for src_trace in src_traces:
            self.all_facts.update(src_trace.all_facts)
        self.score = len(self.all_facts)
        
    def flatten(self, skip_fact_ids=[]):
        all_traces = self._get_all_traces()
        skip_fact_ids = set(skip_fact_ids)
        # Sort by fact ID is necessarily a valid topological sort
        for fact in sorted(self.all_facts, key=lambda f:f._clips_index()):
            if fact._clips_index() not in skip_fact_ids:
                trace = all_traces[fact]
                yield fact, trace.rule, [t.fact for t in trace.src_traces]
        
    def _get_all_traces(self):
        all_traces = {self.fact: self}
        for src_trace in self.src_traces:
            all_traces.update(src_trace._get_all_traces())
        return all_traces
            
    def _recursive_str(self, indent=0):
        header = '{}{} {} [{}]'.format(indent, self.fact._name, self.fact._as_dict(), 
                                     'Input' if self.rule is None else self.rule.name)
        indent += '  '
        return '<{}>'.format('\n'.join([header] + [t._recursive_str(indent) for t in self.src_traces]))


class BackwardTraceFinder(object):
    MAX_BRANCHES = 1000
    
    def __init__(self, activation_log):
        self._activation_log = activation_log
        self._fact_map = defaultdict(list)
        for rule, src_facts, target_fact in activation_log.get_activations():
            if target_fact is not None:
                self._fact_map[target_fact._clips_index()].append((rule, src_facts))
        self._cache = {}
        self._known_fact_indices = set()
        
    def get_activations_for_fact(self, fact_id):
        return self._fact_map[fact_id]
        
    def add_known_fact_indices(self, fact_indices):
        self._known_fact_indices.update(fact_indices)
        self._cache.clear()

    def trace(self, fact_type, fact_args, num=1):
        if isinstance(fact_type, basestring):
            fact_type = self._activation_log.engine.clips_types[fact_type]
        fact = self._activation_log.find_fact(fact_type, **fact_args)
        if fact is None:
            raise FactNotFoundError((fact_type, fact_args))
        return self._cached_trace(fact, num)
    
    def _cached_trace(self, fact, num):
        cache = self._cache.setdefault(num, {})
        if fact in cache:
            return cache[fact]
        result = self._trace(fact, num)
        cache[fact] = result
        return result
    
    def _trace(self, fact, num):
        if fact._clips_obj.Index in self._known_fact_indices:
            return [Trace(fact)]
        
        best_traces = []
        fact_id = fact._clips_index()
        for rule, src_facts in self._fact_map[fact_id]:
            if max(src_fact._clips_index() for src_fact in src_facts) >= fact_id:
                # Suboptimal, but problem is very difficult otherwise 
                continue
            src_traces = [self._cached_trace(src_fact, num) for src_fact in src_facts]
            for n, sources in enumerate(product(*src_traces)):
                if n >= self.MAX_BRANCHES: break
                new_trace = Trace(fact, rule, sources)
                index = bisect([t.score for t in best_traces], new_trace.score)
                if index < num:
                    best_traces.insert(index, new_trace)
                    best_traces[num:] = []
        
        return best_traces
