.. HucitLib documentation master file, created by
   sphinx-quickstart on Wed Sep 23 11:05:47 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to HucitLib's documentation!
====================================

``hucitlib`` is a knowledge base about classical (Greek and Latin) texts, as
well as a Python library to query and modify its contents.

The main goal of ``hucitlib`` is to support the automatic extraction of
bibliographic references to primary sources in the domain of Classics. The ``hucitlib``
knowledge base contains:

- names (and abbreviations) of ancient authors;
- titles (and abbreviations) of ancient works;
- resolvable URIs and unique identifiers (CTS URNs) for authors, works and citable passages;
- links to external resources (Perseus Catalog, Wikidata, Wikipedia);
- information about the canonical citation structure of ancient works.

``hucitlib`` relies on `SuRF <https://pythonhosted.org/SuRF/>`_ , a Python Object RDF Mapper library, so as to In order to make the
knowledge base as much as possible easy to use programmatically. `SuRF <https://pythonhosted.org/SuRF/>`_
works similarly to Object-relation mappers (such as SQLAlchemy) with the main difference that Python objects
are mapped to contents of a triples store rather than of a database. This allows for
programmatic interaction with the knowledge base, and makes it possible to hide away certain
complexities of the underlying data model.

If you are using ``hucitlib`` as part of your research, please cite the
`following paper <http://ceur-ws.org/Vol-2014/paper-01.pdf>`_:

.. code-block:: bibtex

    @inproceedings{DBLP:conf/semweb/RomanelloP17,
    author    = {Matteo Romanello and
                 Michele Pasin},
    editor    = {Alessandro Adamou and
                 Enrico Daga and
                 Leif Isaksen},
    title     = {Using Linked Open Data to Bootstrap a Knowledge Base of Classical
                 Texts},
    booktitle = {Proceedings of the Second Workshop on Humanities in the Semantic Web
                 (WHiSe {II)} co-located with 16th International Semantic Web Conference
                 {(ISWC} 2017), Vienna, Austria, October 22, 2017},
    series    = {{CEUR} Workshop Proceedings},
    volume    = {2014},
    pages     = {3--14},
    publisher = {CEUR-WS.org},
    year      = {2017},
    url       = {http://ceur-ws.org/Vol-2014/paper-01.pdf},
    timestamp = {Wed, 12 Feb 2020 16:44:52 +0100},
    biburl    = {https://dblp.org/rec/conf/semweb/RomanelloP17.bib},
    bibsource = {dblp computer science bibliography, https://dblp.org}
  }

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   setup
   model
   cli
   kb
   surf_mappings



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
