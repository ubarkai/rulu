from rulu.engine import RuleEngine

engine = RuleEngine()
engine.load_module('family')
engine.load('family-in.clp')
engine.run()
engine.save('family-out.clp')
