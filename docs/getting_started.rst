.. _`Getting Started`:

===============
Getting Started
===============
In this demo we'll define a **Family Tree** expert system, that takes as input 
low-level information about family relations ("X is the father of Y", 
"Y is the father of Z") and **deduces** higher-level relations ("X is 
the grandfather of Z").

Step 1: Define the data model
-----------------------------
The basic unit of information for the rule engine is the **fact**, which is 
simply a record containing one or more data fields. Facts are **structured**, 
so we need to start by defining the fields contained in each fact type. This 
translates to **template** definitions in CLIPS, and is analogous to 
**relation/table** definitions in an RDBMS.

.. code-block:: python

    from rulu import *
    
    class IsFatherOf(Fact):
        father = StringField()
        son = StringField()

Step 2: Define rules
--------------------
At the core of the expert system are the **rule definitions**. They provide the
**business logic** for generating new facts based on known ones, according to
various conditions.

We'll now define a rule that states the following: If *X* is the father of
*Y*, and *Y* is the father of *Z*, then *X* is the grandfather of *Z*.

.. code-block:: python

    IsGrandfatherOf = RuleDef(
       match(IsFatherOf[1].son, IsFatherOf[2].father),
       action(Assert(grandfather=IsFatherOf[1].father, grandson=IsFatherOf[2].son, degree=0)) 
    )

Let's break this definition to its different components:

1. This rule takes as input **two** facts of type ``IsFatherOf``. They are 
   referred to as '1' and '2' (but any name may be used).
2. The only condition is expressed in the **match** statement. It states
   that the ``son`` member of record #1 needs to equal the ``father`` member
   of record #2. Continuing the RDBMS analogy, a **match** statement is
   similar to a **JOIN** between tables.
3. Whenever the **match** condition holds, the rule is fired, and its actions
   are taken. In this case we use a single **Assert** action, which is the CLIPS
   terminology for creating new facts.
4. The above rule also contains an **implicit** definition for a fact type named
   ``IsGrandfatherOf`` with 3 fields (``grandfather``, ``grandson``, ``degree``).
   
Let's add another rule, to cover great-grandfathers of all degrees.

.. code-block:: python

    RuleDef(
        target(IsGrandfatherOf),
        match(IsFatherOf.son, IsGrandfatherOf.grandfather),
        action(Assert(grandfather=IsFatherOf.father, 
                      grandson=IsGrandfatherOf.grandson, 
                      degree=IsGrandfatherOf.degree+1)) 
    )

Notes:
    
5. In the rule we used the **target** statement to specify explicitly the
   target fact type.
6. In the arithmetic expression ``IsGrandfatherOf.degree+1``, it is important
   to note that the actual calculation will not run in Python. In fact,
   this example contains **pure CLIPS rules** in the sense that **no Python code** 
   will run during rule engine execution. the Instead, Rulu will "compile" these rule 
   definitions to CLIPS code, and CLIPS will take care of the entire run. This is great
   for large data sets because CLIPS (written in C) is **by far** more efficient than
   Python.   

 
Step 3: Add input facts
-----------------------
.. code-block:: python

    from rulu.engine import RuleEngine
    
    engine = RuleEngine()
    # Load the data model and rules (assuming they're defined in 'family.py')
    engine.load_module('family')
    
    engine.assert_('IsFatherOf', father='Adam', son='Seth')
    engine.assert_('IsFatherOf', father='Seth', son='Enos')
    engine.assert_('IsFatherOf', father='Enos', son='Kenan')
    engine.assert_('IsFatherOf', father='Kenan', son='Mahalalel')

Step 4: Run the rule engine
---------------------------
.. code-block:: python

    # Apply all rules while possible
    engine.run()

    
Step 5: Read the output facts
-----------------------------
.. code-block:: python

    # Print output facts
    for fact in engine.get_facts('IsGrandfatherOf'):
        print '{} is the {}grandfather of {}.'.format(
                fact.grandfather, 'great-'*fact.degree, fact.grandson)

Output
------
.. include:: examples/family-out.txt
    :code: python
    :literal:
