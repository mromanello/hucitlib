# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com
import logging
import pytest
import pickle

logger = logging.getLogger(__name__)

@pytest.mark.run(order=1)
def test_kb_virtuoso(kb_virtuoso):
    logger.debug(kb_virtuoso)
    authors = kb_virtuoso.get_authors()
    for author in authors[:10]:
        logger.info("%s" % author)
    iliad = kb_virtuoso.get_resource_by_urn("urn:cts:greekLit:tlg0012.tlg001")
    logger.info(iliad.author)

@pytest.mark.run(order=2)
def test_pickle_kb_inmemory(kb_inmemory):
    pre_pickling_author_number = len(kb_inmemory.get_authors())
    pickled_kb = pickle.dumps(kb_inmemory)
    unpickled_kb = pickle.loads(pickled_kb)
    assert len(unpickled_kb.get_authors()) == pre_pickling_author_number

@pytest.mark.run(order=3)
def test_kb_inmemory(kb_inmemory):
    logger.debug(kb_inmemory)
    authors = kb_inmemory.get_authors()
    for author in authors[:10]:
        logger.info("%s" % author)
    iliad = kb_inmemory.get_resource_by_urn("urn:cts:greekLit:tlg0012.tlg001")
    logger.info("%s" % iliad.author)

@pytest.mark.run(order=4)
def test_kb_author_names(kb_virtuoso):
    names = kb_virtuoso.author_names
    assert names is not None and len(names) > 0
    logger.info("%i unique author names found in the KB" % len(names))

@pytest.mark.run(order=5)
def test_kb_author_abbreviations(kb_virtuoso):
    abbreviations = kb_virtuoso.author_abbreviations
    assert abbreviations is not None and len(abbreviations) > 0
    logger.info("%i abbreviations of author names found in the KB" % len(abbreviations))
    for i, author_key in enumerate(abbreviations.keys()[:10]):
        logger.info("%i. %s => %s" % (i, author_key.split("$$")[0], abbreviations[author_key]))

@pytest.mark.run(order=5)
def test_kb_get_titles(kb_virtuoso):
    titles = kb_virtuoso.work_titles
    assert titles is not None and len(titles) > 0
    logger.info("%i work titles found in the KB" % len(titles))

@pytest.mark.run(order=6)
def test_kb_work_abbreviations(kb_virtuoso):
    abbreviations = kb_virtuoso.work_abbreviations
    assert abbreviations is not None and len(abbreviations) > 0
    logger.info("%i abbreviations of work titles found in the KB" % len(abbreviations))

@pytest.mark.run(order=7)
def test_kb_get_statistics(kb_virtuoso):
    stats = kb_virtuoso.get_statistics()
    logger.info(stats)
    assert stats is not None and 0 not in stats.values()
