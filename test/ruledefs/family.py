from rulu import *

# Data model definition for "X is the father of Y"
class IsFatherOf(Fact):
    father = StringField()
    son = StringField()

# Rule #1: if X is the father of Y, and Y is the father of Z,
#          then X is the grandfather of Z.
# Implicitly defines the data model for IsGrandfatherOf.
IsGrandfatherOf = RuleDef(
    # This rule matches (joins) two existing facts of type IsFatherOf
    match(IsFatherOf[1].son, IsFatherOf[2].father),
    action(Assert(grandfather=IsFatherOf[1].father, 
                  grandson=IsFatherOf[2].son, 
                  greatness=0)) 
)

# Rule #2: if X is the father of Y, and Y is the (great-...)grandfather of Z,
#          then X is also the great-(great-...)grandfather of Z.
RuleDef(
    target(IsGrandfatherOf),
    match(IsFatherOf.son, IsGrandfatherOf.grandfather),
    action(Assert(grandfather=IsFatherOf.father, 
                  grandson=IsGrandfatherOf.grandson, 
                  greatness=IsGrandfatherOf.greatness+1)) 
)
