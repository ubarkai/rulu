from rulu import *

@IntegerRuleFunc
def zero():
    return 0

@RuleFunc
def increment(x):
    return x+1

@RuleFunc
def take_father(x):
    return x.father

class IsFather(Fact):
    father = StringField()
    son = StringField()

IsGrandfather = RuleDef(
    match(IsFather[0].son, IsFather[1].father),
    action(Assert(grandfather=IsFather[0].father, grandson=IsFather[1].son, great=zero()))
)

RuleDef(
    target(IsGrandfather),
    match(IsFather.son, IsGrandfather.grandfather),
    action(Assert(grandfather=take_father(IsFather), grandson=IsGrandfather.grandson, great=increment(IsGrandfather.great)))
)
