from rulu import *


class Pair(Fact):
    first = IntegerField()
    second = IntegerField()


class Dummy(Fact):
    x = IntegerField()


PairSum = RuleDef(
    foreach(Pair),
    match(Pair.first, Dummy.x),
    not_exists(Dummy),
    action(Assert(sum=Pair.first+Pair.second))
)
