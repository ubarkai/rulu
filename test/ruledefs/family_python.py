from rulu import *

class IsFather(Fact):
    father = StringField()
    son = StringField()

IsGrandfather = RuleDef(
    fields(grandfather=String, grandson=String, great=Integer),
    match(IsFather[0].son, IsFather[1].father)
)

@IsGrandfather._python_action
def action(assert_, IsFather):
    assert_(grandfather=IsFather[0].father, grandson=IsFather[1].son, great=0)

GreatGrandfather = RuleDef(
    target(IsGrandfather),
    match(IsFather.son, IsGrandfather.grandfather)
)
@GreatGrandfather._python_action
def action2(assert_, IsFather, IsGrandfather):
    assert_(grandfather=IsFather.father, grandson=IsGrandfather.grandson, great=IsGrandfather.great+1)
