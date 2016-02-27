from rulu import *

# Declare a built-in CLIPS function by name and return value.
strcat = clips_func('str-cat', String)

class Entity(Fact):
    name = StringField()
    
Greeting = RuleDef(
    action(Assert(text=strcat("Hello, ", Entity.name, "!")))
)
