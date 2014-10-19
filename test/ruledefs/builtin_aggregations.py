from rulu import *

class Pair(Fact):
    first = IntegerField()
    second = IntegerField()

SumByFirst = RuleDef(
    groupby(first=Pair.first),
    action(AssertAggregate(value=Sum(Pair.second)))
)

MaxByFirst = RuleDef(
    groupby(first=Pair.first + 0), # Group by general expression
    action(AssertAggregate(value=Max(Pair.second)))
)

ArgMinMax = RuleDef(
    groupby(first=Pair.first),
    action(AssertAggregate(argmin=ArgMin(Pair.second, key=Pair.second*(-1)+10),
                           argmax=ArgMax(Pair.second, key=Pair.second+10)))
)

CountAll = RuleDef(
    foreach(Pair),
    action(AssertAggregate(value=Count()))
)
