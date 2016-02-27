========
Fact I/O
========

In the :ref:`basic example` we used Python code to insert input facts into the expert system's 
working memory. We also used Python code to process the output facts directly. It is often
useful to import/export facts from/to other formats for integration with other data processing 
tools (or simply for storage on disk).

CLIPS format
------------
The native CLIPS format can be used for storing facts in files:

.. include:: examples/save_load.py
    :code: python
    :literal:
    
**family-in.clp**

.. include:: examples/family-in.clp
    :code:
    :literal:

**family-out.clp**

.. include:: examples/family-out.clp
    :code:
    :literal:


Pandas dataframes
-----------------
The dataframe is a very convenient structure for holding fact data:

.. include:: examples/export_pd.py
    :code: python
    :literal: 

Export to Excel
---------------


Database integration
--------------------
TBD :)
