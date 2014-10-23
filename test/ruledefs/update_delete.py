from rulu import *

class Pair(Fact):
    first = IntegerField()
    second = IntegerField()


SumByFirst = RuleDef(
    # Added extra _id field to ensure fact uniqueness
    action(Assert(first=Pair.first, value=Pair.second, _id=Pair.second))
)

RuleDef(
    match(SumByFirst[0].first, SumByFirst[1].first),
    condition(fact_index(SumByFirst[0]) != fact_index(SumByFirst[1])),
    action(Update(SumByFirst[0], value=SumByFirst[0].value + SumByFirst[1].value)),
    action(Delete(SumByFirst[1]))
)

MaxByFirst = RuleDef(
    action(Assert(first=Pair.first, value=Pair.second))
)

for i in (0, 1):
    RuleDef(
        match(MaxByFirst[0].first, MaxByFirst[1].first),
        condition(MaxByFirst[i].value < MaxByFirst[1-i].value),
        action(Delete(MaxByFirst[i]))
    )
