import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand
from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'VERSION')) as version_file:
    version = version_file.read().strip()
    

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)
    

setup(
    name='rulu',
    version=version,
    url='http://github.com/ubarkai/rulu',
    license='???',
    author='Uri Barkai',
    author_email='ubarkai@gmail.com',
    description='Python interface for building rule-based expert systems over PyCLIPS',
    install_requires = ['bunch'],
    tests_require=['pytest'],
    extras_require={'testing': ['pytest']},
    cmdclass={'test': PyTest},
    test_suite='test.test_ruleengine',
    packages=['rulu']
)
