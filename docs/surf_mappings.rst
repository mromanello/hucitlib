Surf mappings
=============

``hucitlib`` relies on `SuRF <https://pythonhosted.org/SuRF/>`_ , a Python Object RDF Mapper library, so as to In order to make the
knowledge base as much as possible easy to use programmatically. `SuRF <https://pythonhosted.org/SuRF/>`_
works similarly to Object-relation mappers (such as SQLAlchemy) with the main difference that Python objects
are mapped to contents of a triples store rather than of a database.

A set of `SuRF <https://pythonhosted.org/SuRF/>` mappings is defined in order to ease the
programmatic interaction with the knowledge base, and to away certain complexities of the
underlying :ref:`data model`.

Mappings are defined for the following classes:

- ``frbroo:F10_Person`` -> :py:class:`~hucitlib.surfext.HucitAuthor`
- ``frbroo:F1_Work`` -> :py:class:`~hucitlib.surfext.HucitWork`
- ``hucit:TextElement`` -> :py:class:`~hucitlib.surfext.HucitTextElement`
- ``hucit:TextStructure`` -> :py:class:`~hucitlib.surfext.HucitTextStructure`

Authors
-------

.. autoclass:: hucitlib.surfext.HucitAuthor
    :members:

Works
-----

.. autoclass:: hucitlib.surfext.HucitWork
    :members:

Citable text structures and text elements
-----------------------------------------

.. autoclass:: hucitlib.surfext.HucitTextStructure
    :members:

.. autoclass:: hucitlib.surfext.HucitTextElement
    :members:
