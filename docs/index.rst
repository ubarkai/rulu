.. Rulu documentation master file, created by
   sphinx-quickstart on Sun Jun 15 11:27:36 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==================
Rulu Documentation
==================

Rulu provides a Pythonic, declarative interface for building rule-based expert
systems. 

Rulu is implemented over `PyCLIPS`_, the Python wrapper of the `CLIPS`_ expert
system library.

.. _PyCLIPS: http://pyclips.sourceforge.net/web/
.. _CLIPS: http://clipsrules.sourceforge.net/

.. toctree::
   :maxdepth: 2

Installation
============
1. Download **PyCLIPS** from `here`_
2. Install **PyCLIPS**: ``python setup.py install``
3. ``pip install rulu``

.. _here: http://sourceforge.net/projects/pyclips/files/pyclips/pyclips-1.0/

Example
=======
Here is an expert system for family trees!

Data Model and Rule Definitions
-------------------------------
**family.py**

.. include:: ../test/ruledefs/family.py
    :code: python
    :literal:

Rule Engine Execution
---------------------
**main.py**

.. include:: examples/example1.py
    :code: python
    :literal:

Output
------

.. code-block:: python

    Enos is the grandfather of Mahalalel.
    Seth is the great-grandfather of Mahalalel.
    Adam is the great-great-grandfather of Mahalalel.
    Seth is the grandfather of Kenan.
    Adam is the great-grandfather of Kenan.
    Adam is the grandfather of Enos.
