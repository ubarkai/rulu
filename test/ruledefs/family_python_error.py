from rulu import *

@RuleFunc
def error():
    raise RuntimeError

class IsFather(Fact):
    father = StringField()
    son = StringField()


IsGrandfather = RuleDef(
    match(IsFather[0].son, IsFather[1].father),
    action(Assert(grandfather=IsFather[0].father, grandson=IsFather[1].son, great=error()))
)
