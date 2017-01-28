# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com
import logging
import pytest
from knowledge_base import KnowledgeBase
from pytest import fixture
import pdb


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@fixture
def kb_inmemory(configuration_file="inmemory.ini"):
	if(configuration_file is not None):
		return KnowledgeBase(configuration_file)
@fixture
def kb_virtuoso(configuration_file="virtuoso.ini"):
	if(configuration_file is not None):
		return KnowledgeBase(configuration_file)
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


