from rulu import *

@RuleFunc
def error():
    raise RuntimeError

class IsFatherOf(Fact):
    father = StringField()
    son = StringField()


IsGrandFatherOf = RuleDef(
    match(IsFatherOf[0].son, IsFatherOf[1].father),
    action(Assert(grandfather=IsFatherOf[0].father, grandson=IsFatherOf[1].son, greatness=error()))
)
