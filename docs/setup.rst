Setup
=====

Installation
------------

.. code-block:: bash

  pip install hucitlib


Default triple store
--------------------

By default, when initialising a :py:class:`hucitlib.KnowledgeBase` instance, RDF
data are read from a read-only public triple store, which runs
on the CLARIAH Druid infrastructure:

.. code-block:: python

  >>> from hucitlib import KnowledgeBase
  >>> kb = KnowledgeBase()
  >>> kb.settings
  {
    'reader': 'sparql_protocol',
    'writer': 'sparql_protocol',
    'endpoint': 'https://api.druid.datalegend.net/datasets/mromanello/hucit/services/hucit/sparql',
    'default_context': 'https://druid.datalegend.net/mromanello/hucit/graphs/default'
  }

.. note::

  When connecting to the default triple store, all methods that modify entries in the
  knowledge base (e.g. :py:meth:`hucitlib.surfext.HucitAuthor.set_urn`) won't work!

Connecting to a local triple store
----------------------------------

The RDF data that power ``hucitlib`` can be stored in any triple store that
supports the SPARQL 1.1 API.
``hucitlib`` comes with scripts to `install <https://github.com/mromanello/hucitlib/blob/master/install_3stores.sh>`_
and `load/clear/dump <https://github.com/mromanello/hucitlib/tree/master/scripts/virtuoso>`_ data from a Virtuoso triples store.

If you prefer to use another triple store, after having it set up and loaded the data into it, just create
a new configuration file

.. code-block:: python

  # content of virtuoso_local.ini
  [surf]
  reader=sparql_protocol
  writer=sparql_protocol
  server=localhost
  endpoint=http://localhost:8890/sparql
  port=8890
  default_context=http://purl.org/hucit/kb

and pass the path to this file when initialising the knowledge base

.. code-block:: python

  >>> from hucitlib import KnowledgeBase
  >>> kb = KnowledgeBase('virtuoso_local.ini')
  >>> kb.settings
  {
    'reader': 'sparql_protocol',
    'writer': 'sparql_protocol',
    'server': 'localhost',
    'endpoint': 'http://localhost:8890/sparql',
    'port': 8890,
    'default_context': 'http://purl.org/hucit/kb'
  }
