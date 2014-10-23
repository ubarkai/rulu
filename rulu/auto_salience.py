from collections import defaultdict
from fact import IndexedFactReference
from utils import RuleEngineError

def auto_set_salience(ruledefs):
    dependencies = _get_dependencies(ruledefs)
    order = _topological_sort(dependencies)
    for n, rule in enumerate(order):
        rule.set_salience(-(n*2))
    
def _get_dependencies(ruledefs):
    by_target = defaultdict(list)
    for ruledef in ruledefs:
        by_target[ruledef._rule.target].append(ruledef._rule)
        by_target[ruledef._rule.target].extend(ruledef._rule.secondary_rules)

    dependencies = defaultdict(set)
    for ruledef in ruledefs:
        for premise in ruledef._rule.premises:
            if isinstance(premise, IndexedFactReference):
                premise = premise._template_cls
            for other_rule in by_target[premise]:
                if other_rule is not ruledef._rule:
                    dependencies[other_rule].add(ruledef._rule)
    return dependencies

# Adapted from networkx (https://networkx.github.io)
def _topological_sort(dependencies):
    seen = set()
    order = []
    explored = set()

    for v in dependencies.keys():     # process all vertices
        if v in explored:
            continue
        fringe = [v]   # nodes yet to look at
        while fringe:
            w = fringe[-1]  # depth first search
            if w in explored: # already looked down this branch
                fringe.pop()
                continue
            seen.add(w)     # mark as seen
            # Check successors for cycles and for new nodes
            new_nodes = []
            for n in dependencies[w]:
                if n not in explored:
                    if n in seen: #CYCLE !!
                        raise RuleEngineError("Dependencies graph contains a cycle, cannot set salience automatically.")
                    new_nodes.append(n)
            if new_nodes:   # Add new_nodes to fringe
                fringe.extend(new_nodes)
            else:           # No new nodes so w is fully explored
                explored.add(w)
                order.append(w)
                fringe.pop()    # done considering this node
    return list(reversed(order))
