# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com
import logging
import sys
import pytest
from pytest import fixture
import pkg_resources
import knowledge_base
from knowledge_base import *
#from surf.log import setup_logger, set_logger_level
#setup_logger()
#set_logger_level(logging.DEBUG)
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger()


@fixture(scope="session")
def kb_inmemory(filename="inmemory.ini"):
	configuration_file = pkg_resources.resource_filename('knowledge_base','config/%s'%filename)
	logger.info("Using config file: %s"%configuration_file)
	return KnowledgeBase(configuration_file)
	
@fixture(scope="session")
def kb_virtuoso(filename="virtuoso.ini"):
	configuration_file = pkg_resources.resource_filename('knowledge_base','config/%s'%filename)
	logger.info("Using config file: %s"%configuration_file)
	return KnowledgeBase(configuration_file)
