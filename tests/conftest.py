# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com
import logging
import sys
import pytest
from pytest import fixture
from knowledge_base import *

from surf.log import setup_logger, set_logger_level
setup_logger()
set_logger_level(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger()


@fixture
def kb_inmemory(configuration_file="inmemory.ini"):
	if(configuration_file is not None):
		return KnowledgeBase(configuration_file)
@fixture
#@pytest.mark.skip(reason="need to deal with installing virtuoso at build-time")
def kb_virtuoso(configuration_file="virtuoso.ini"):
	if(configuration_file is not None):
		return KnowledgeBase(configuration_file)
