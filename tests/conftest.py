# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com
import os
import logging
import pathlib
import sys
import pytest
from pytest import fixture
import pkg_resources
import hucitlib
from hucitlib import *

OUTPUT_DIR = pkg_resources.resource_filename(
    "hucitlib", f"data/tests/"
)

pathlib.Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
log_file_path = os.path.join(OUTPUT_DIR, 'tests.log')

#####################
#   LOGGING CONFIG  #
#####################

# from surf.log import setup_logger, set_logger_level
# setup_logger()
# set_logger_level(logging.DEBUG)
#logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename=log_file_path, mode='w')
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

filename = "virtuoso_pc6.ini"
DEFAULT_CONFIG_FILE = pkg_resources.resource_filename("hucitlib", f"config/{filename}")


@fixture(scope="session")
def kb_inmemory(filename="inmemory.ini"):
    configuration_file = pkg_resources.resource_filename(
        "hucitlib", "config/%s" % filename
    )
    logger.info("Using config file: %s" % configuration_file)
    return KnowledgeBase(configuration_file)


@fixture(scope="session")
def kb_virtuoso(filename="virtuoso_pc6.ini"):
    configuration_file = pkg_resources.resource_filename(
        "hucitlib", "config/%s" % filename
    )
    logger.info("Using config file: %s" % configuration_file)
    return KnowledgeBase(configuration_file)
