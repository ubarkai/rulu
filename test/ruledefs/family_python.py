from rulu import *

class IsFatherOf(Fact):
    father = StringField()
    son = StringField()

IsGrandfatherOf = RuleDef(
    fields(grandfather=String, grandson=String, greatness=Integer),
    match(IsFatherOf[0].son, IsFatherOf[1].father)
)

@IsGrandfatherOf._python_action
def action(assert_, IsFatherOf):
    assert_(grandfather=IsFatherOf[0].father, grandson=IsFatherOf[1].son, greatness=0)

greatnessGrandfather = RuleDef(
    target(IsGrandfatherOf),
    match(IsFatherOf.son, IsGrandfatherOf.grandfather)
)
@greatnessGrandfather._python_action
def action2(assert_, IsFatherOf, IsGrandfatherOf):
    assert_(grandfather=IsFatherOf.father, grandson=IsGrandfatherOf.grandson, greatness=IsGrandfatherOf.greatness+1)
