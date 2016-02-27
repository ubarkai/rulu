.. Rulu documentation master file, created by
   sphinx-quickstart on Sun Jun 15 11:27:36 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==================
Rulu Documentation
==================

Rulu provides a Pythonic, declarative interface for building rule-based `expert systems`_. 

Rulu is implemented over `PyCLIPS`_, the Python wrapper of the `CLIPS`_ expert
system library.

.. _expert systems: http://clipsrules.sourceforge.net/WhatIsCLIPS.html#ExpertSystems
.. _PyCLIPS: http://pyclips.sourceforge.net/web/
.. _CLIPS: http://clipsrules.sourceforge.net/

Installation
============
``pip install rulu``

User Documentation
==================

.. toctree::
    :maxdepth: 2

    getting_started
    python_code
    clips_funcs
    update_delete
    aggregations
    python_aggregations    
    multifields
    fact_io
