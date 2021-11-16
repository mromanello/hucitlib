Knowledge base
===================

The class :py:class:`~hucitlib.KnowledgeBase` is the main access point to all resources
described in the knowledge base (e.g. :py:class:`~hucitlib.surfext.HucitAuthor`,
:py:class:`~hucitlib.surfext.HucitWork`, etc.). Its methods can be divided into the following high-level groups:

- methods that concern globally the knowledge base:

  - :py:meth:`~hucitlib.KnowledgeBase.search`
  - :py:meth:`~hucitlib.KnowledgeBase.to_json`
  - :py:meth:`~hucitlib.KnowledgeBase.get_statistics`

- methods to access top-level resources:

    - :py:meth:`~hucitlib.KnowledgeBase.get_resource_by_urn`
    - :py:meth:`~hucitlib.KnowledgeBase.get_authors`
    - :py:meth:`~hucitlib.KnowledgeBase.get_author_label`
    - :py:meth:`~hucitlib.KnowledgeBase.get_works`
    - :py:meth:`~hucitlib.KnowledgeBase.get_work_label`
    - :py:meth:`~hucitlib.KnowledgeBase.get_opus_maximum_of`
    - :py:meth:`~hucitlib.KnowledgeBase.get_textelement_type`
    - :py:meth:`~hucitlib.KnowledgeBase.get_textelement_types`

- "factory methods", i.e. methods that create new objects (i.e. entries):

    - :py:meth:`~hucitlib.KnowledgeBase.create_cts_urn`
    - :py:meth:`~hucitlib.KnowledgeBase.create_text_element`
    - :py:meth:`~hucitlib.KnowledgeBase.add_textelement_type`
    - :py:meth:`~hucitlib.KnowledgeBase.add_textelement_types`

.. autoclass:: hucitlib.KnowledgeBase
    :members:
