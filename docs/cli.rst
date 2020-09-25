Command line interface
======================

``HucitLib`` comes with a command-line interface to query and modify the knowledge base's contents.

.. code-block:: bash

  $ hucit --help

  RDFLib Version: 5.0.0
  Command line interface for a HuCit knowledge base.

  Usage:
      knowledge_base/cli.py find <search_string> [--config-file=<path>]
      knowledge_base/cli.py add (name|abbr|title|sameas) --to=<cts_urn> <string_to_add> [--config-file=<path>]
      knowledge_base/cli.py (-h | --help)

  Options:
      --to=<cts_urn> CTS URN of the author/work to edit.
      --config-file=<path> Path to the configuration file (overwrites default configuration).

Search
-------------

.. code-block:: bash

  $ hucit find Homer

  Searching for "homer" yielded 2 results

  1) urn:cts:cwkb:498 Homerus Latinus                                    (Matched: 'Homer.')


  2) urn:cts:greekLit:tlg0012 Homer                                      (Matched: 'Homer')
...

Display an entry
----------------
