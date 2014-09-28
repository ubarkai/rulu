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

class IsFatherOf(Fact):
    father = StringField()
    son = StringField()

IsGrandfatherOf = RuleDef(
    match(IsFatherOf[0].son, IsFatherOf[1].father),
    action(Assert(grandfather=IsFatherOf[0].father, grandson=IsFatherOf[1].son, greatness=zero()))
)

RuleDef(
    target(IsGrandfatherOf),
    match(IsFatherOf.son, IsGrandfatherOf.grandfather),
    action(Assert(grandfather=take_father(IsFatherOf), grandson=IsGrandfatherOf.grandson, greatness=increment(IsGrandfatherOf.greatness)))
)
