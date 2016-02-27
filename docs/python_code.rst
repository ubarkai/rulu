.. _`Python Code`:

===================
Running Python Code
===================
The rules in the previous example (see :ref:`Getting Started`) were **pure** CLIPS rules,
that did not involve any Python code during the engine run. Rulu also provides easy
ways to integrate with Python code, as explained here.

Python Actions
--------------
We can write the entire action portion of a rule in python.
For example, compare the **declarative** (CLIPS) rule from the previous section:

.. code-block:: python

    IsGrandfatherOf = RuleDef(
       match(IsFatherOf[1].son, IsFatherOf[2].father),
       action(Assert(grandfather=IsFatherOf[1].father, grandson=IsFatherOf[2].son, degree=0)) 
    )
    
With the following **procedural** (Python) form:

.. code-block:: python

    IsGrandfatherOf = RuleDef(
        fields(grandfather=String, grandson=String, degree=Integer),
        match(IsFatherOf[0].son, IsFatherOf[1].father)
    )
    
    @IsGrandfatherOf._python_action
    def action(assert_, IsFatherOf):
        assert_(grandfather=IsFatherOf[0].father, grandson=IsFatherOf[1].son, degree=0)
        
Notes:

1. Python actions are defined using the ``_python_action`` decorator.
2. The function's parameters include an ``assert_`` function to create new facts,
   as well as all the input facts contained in the rule (in this case ``IsFatherOf``
   accessible as a dictionary).
3. Note the explicit **fields** declaration. In the previous example, Rulu could automatically 
   deduce the target fields from the ``Assert`` statement. Here the fact assertion is done in 
   run-time, so the fields cannot be deduced up front and need to be declared.

Python Functions
----------------
We can use Python code even when writing rules using the declarative (CLIPS) form.
The functions need to be **registered** in advance, as follows:

.. code-block:: python

    @RuleFunc
    def increment(x):
        return x+1
    
    @RuleFunc
    def take_father(x):
        return x.father
    
    RuleDef(
        target(IsGrandfatherOf),
        match(IsFatherOf.son, IsGrandfatherOf.grandfather),
        action(Assert(grandfather=take_father(IsFatherOf), grandson=IsGrandfatherOf.grandson, greatness=increment(IsGrandfatherOf.greatness)))
    )

Note: in this case the function return types can be deduced from context. In other cases
they have to be declared explicitly using ``@IntegerRuleFunc``, ``StringRuleFunc`` etc.
