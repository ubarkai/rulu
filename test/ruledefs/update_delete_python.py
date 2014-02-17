from rulu import *

class Pair(Fact):
    first = IntegerField()
    second = IntegerField()

SumByFirst = RuleDef(
    action(Assert(first=Pair.first, value=Pair.second))
)

add_to_sum = RuleDef(
    match(SumByFirst[0].first, SumByFirst[1].first),
    condition(clips_funcs.fact_index(SumByFirst[0]) != 
              clips_funcs.fact_index(SumByFirst[1]))
)

@add_to_sum._python_action
def _add_to_sum(SumByFirst):
    SumByFirst[0]._update(value=SumByFirst[0].value + SumByFirst[1].value)
    SumByFirst[1]._delete()


MaxByFirst = RuleDef(
    action(Assert(first=Pair.first, value=Pair.second))
)

update_max = RuleDef(
    match(MaxByFirst[0].first, MaxByFirst[1].first)
)

@update_max._python_action
def _update_max(MaxByFirst):
    diff = MaxByFirst[0].value - MaxByFirst[1].value
    if diff != 0:
        MaxByFirst[diff > 0]._delete()
