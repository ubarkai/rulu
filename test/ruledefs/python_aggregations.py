from collections import defaultdict
from rulu import *

class Pair(Fact):
    first = IntegerField()
    second = IntegerField()

SumByFirst = RuleDef(
    fields(first=Integer, value=Integer),
    foreach(Pair)
)

@SumByFirst._aggregator
class SumByFirstAgg(Aggregator):
    def init(self):
        self.data = defaultdict(lambda : 0)
        
    def process_one(self, Pair):
        self.data[Pair.first] += Pair.second
        
    def finalize(self, assert_):
        for first, total in self.data.items():
            assert_(first=first, value=total)

MaxByFirst = RuleDef(
    fields(first=Integer, value=Integer),
    foreach(Pair)
)
 
@MaxByFirst._groupby(Pair.first)
def calc_max(group, assert_, key):
    assert_(first=key, value=max(pair.second for pair in group))
