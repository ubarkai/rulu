from rulu.engine import RuleEngine
from utils import print_rst_table
engine = RuleEngine()
engine.load_module('greeting')
engine.assert_('Entity', name='World')
print_rst_table(engine, 'Entity', 'greeting-in.txt')
engine.run()
print_rst_table(engine, 'Greeting', 'greeting-out.txt')
