from rulu import *

class TestFact(Fact):
    str = StringField()
    num = IntegerField()

class OutputStr(Fact):
    str = StringField()

class OutputNum(Fact):
    num = IntegerField()

OutputNum = RuleDef(
    match(TestFact.str, "a"),
    action(Assert(num=TestFact.num))
)

OutputStr = RuleDef(
    match(TestFact.num, 2),
    action(Assert(str=TestFact.str))
)
