from rulu.engine import RuleEngine

engine = RuleEngine()
# Load the data model and rules
engine.load_module('family')

# Add input facts
engine.assert_('IsFatherOf', father='Adam', son='Seth')
engine.assert_('IsFatherOf', father='Seth', son='Enos')
engine.assert_('IsFatherOf', father='Enos', son='Kenan')
engine.assert_('IsFatherOf', father='Kenan', son='Mahalalel')

# This is where the magic happens
engine.run()

# Print output facts
for fact in engine.get_facts('IsGrandfatherOf'):
    print '{} is the {}grandfather of {}.'.format(
            fact.grandfather, 'great-'*fact.greatness, fact.grandson)
