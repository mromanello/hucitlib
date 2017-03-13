# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com
import logging
import pytest
import pdb


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.mark.skip(reason="need to deal with installing virtuoso at build-time")
def test_kb_virtuoso(kb_virtuoso):
	logger.debug(kb_virtuoso)
	authors = kb_virtuoso.get_authors()
	for author in authors[:10]:
		logger.info("%s"%author)
	iliad = kb_virtuoso.get_resource_by_urn("urn:cts:greekLit:tlg0012.tlg001")
	logger.info(iliad.author)
def test_kb_inmemory(kb_inmemory):
	logger.debug(kb_inmemory)
	authors = kb_inmemory.get_authors()
	#pdb.set_trace()
	for author in authors[:10]:
		logger.info("%s"%author)
	iliad = kb_inmemory.get_resource_by_urn("urn:cts:greekLit:tlg0012.tlg001")
	logger.info("%s"%iliad.author)
def test_kb_author_names(kb_inmemory):
	names = kb_inmemory.author_names
	assert names is not None and len(names) > 0
	logger.info("%i unique author names found in the KB"%len(names))
def test_kb_author_abbreviations(kb_inmemory):
	abbreviations = kb_inmemory.author_abbreviations
	assert abbreviations is not None and len(abbreviations) > 0
	logger.info("%i abbreviations of author names found in the KB"%len(abbreviations))
	for i, author_key in enumerate(abbreviations.keys()[:10]):
		logger.info("%i. %s => %s"%(i, author_key.split("$$")[0], abbreviations[author_key]))
def test_kb_get_titles(kb_inmemory):
	titles = kb_inmemory.work_titles
	assert titles is not None and len(titles) > 0
	logger.info("%i work titles found in the KB"%len(titles))
def test_kb_work_abbreviations(kb_inmemory):
	abbreviations = kb_inmemory.work_abbreviations
	assert abbreviations is not None and len(abbreviations) > 0
	logger.info("%i abbreviations of work titles found in the KB"%len(abbreviations))
def test_kb_get_statistics(kb_inmemory):
	stats = kb_inmemory.get_statistics()
	assert stats is not None and not 0 in stats.values()
"""
Tests to write (each tests against both knowledge flavours):

- test_get_statistics
- test remove
"""