from rulu import *

class Pair(Fact):
    first = IntegerField()
    second = IntegerField()

SumByFirst = RuleDef(
    groupby(first=Pair.first),
    action(AssertAggregate(value=Sum(Pair.second)))
)

MaxByFirst = RuleDef(
    groupby(first=Pair.first),
    action(AssertAggregate(value=Max(Pair.second)))
)

CountAll = RuleDef(
    foreach(Pair),
    action(AssertAggregate(value=Count(1)))
)
