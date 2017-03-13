# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com
import logging
import pytest
import pdb
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_hucitauthor_to_json(kb_inmemory):
	"""
	Test for `HucitAuthor.to_json()`.
	"""
	homer = kb_inmemory.get_resource_by_urn("urn:cts:greekLit:tlg0012")
	json_string = homer.to_json()
	dict_from_json = json.loads(json_string)
	assert dict_from_json is not None and json_string is not None