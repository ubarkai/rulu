from rulu import *

class Pair(Fact):
    first = IntegerField()
    second = IntegerField()

Grouped = RuleDef(
    groupby(first=Pair.first),
    action(AssertAggregate(values=Concatenate(Pair.second)))
)

@IntegerRuleFunc
def python_sum(values):
    return sum(values)

Sum = RuleDef(
    salience(-10000),
    action(Assert(first=Grouped.first, value=python_sum(Grouped.values)))
)

