import logging
from pkg_resources import resource_filename

from . import inputs
from . import ruledefs
from rulu.engine import RuleEngine
from rulu.rulu_io import facts_to_df
from unittest import TestCase

logging.basicConfig(level=logging.DEBUG)


class RuleEngineIoTests(TestCase):
    def setUp(self):
        self.engine = RuleEngine()
        self.engine.load_module('family', ruledefs)
        self.engine.load(resource_filename(inputs.__name__, 'fathers.txt'))
        
    def test_df(self):
        df = facts_to_df(self.engine, 'IsFatherOf')
        names = 'Adam Seth Enos Kenan Mahalalel'.split()
        self.assertEqual(list(df['father']), names[:-1])
        self.assertEqual(list(df['son']), names[1:])
