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

``hucitlib`` relies on ``SuRF``, a Python Object RDF Mapper library, so as to In order to make the
knowledge base as much as possible easy to use programmatically. ``SuRF`` works similarly to
Object-relation mappers (such as SQLAlchemy) with the main difference that Python objects
are mapped to contents of a triples store rather than of a database. This allows for
programmatic interaction with the knowledge base, and makes it possible to hide away certain
complexities of the underlying data model.

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
