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

Wildcard search works as well:

.. code-block:: bash

  $ hucit find Homer*

  ...

Display
-------

.. code-block:: bash

  $ hucit find urn:cts:greekLit:tlg0011

  Sophokles :: urn:cts:greekLit:tlg0011 (http://purl.org/hucit/kb/authors/1090)

  7 works by this author:
   - Sophokles, Ajax :: urn:cts:greekLit:tlg0011.tlg003                               (http://purl.org/hucit/kb/works/3896)
   - Sophokles, Antigone :: urn:cts:greekLit:tlg0011.tlg002                           (http://purl.org/hucit/kb/works/3897)
   - Sophokles, Electra :: urn:cts:greekLit:tlg0011.tlg005                            (http://purl.org/hucit/kb/works/3898)
   - Sophokles, Oedipus at Kolonos :: urn:cts:greekLit:tlg0011.tlg007                 (http://purl.org/hucit/kb/works/3899)
   - Sophokles, King Oedipus :: urn:cts:greekLit:tlg0011.tlg004                       (http://purl.org/hucit/kb/works/3900)
   - Sophokles, Philoctetes :: urn:cts:greekLit:tlg0011.tlg006                        (http://purl.org/hucit/kb/works/3901)
   - Sophokles, The Women of Trachis :: urn:cts:greekLit:tlg0011.tlg001               (http://purl.org/hucit/kb/works/3902)


  Related resources:
   - http://cwkb.org/author/id/1090/turtle
   - http://data.perseus.org/catalog/urn:cts:greekLit:tlg0011
   - http://viaf.org/viaf/101760867
   - http://www.wikidata.org/wiki/Special:EntityData/Q7235

Edit
----

.. note::

  Editing via CLI is not yet fully implemented/tested.

Changing configuration
----------------------
