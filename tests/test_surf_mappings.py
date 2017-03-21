# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com
import logging
import pytest
import pdb
import json

logger = logging.getLogger(__name__)

# TESTS FOR HUCITAUTHOR
def test_hucitauthor_to_json(kb_inmemory):
	"""
	Test for `HucitAuthor.to_json()`.
	"""
	homer = kb_inmemory.get_resource_by_urn("urn:cts:greekLit:tlg0012")
	json_string = homer.to_json()
	logger.info(json_string)
	dict_from_json = json.loads(json_string)
	assert dict_from_json is not None and json_string is not None
def test_hucitauthor_add_duplicate_name(kb_inmemory):
	"""
	Test to ensure that `HucitAuthor.add_name(...) does not insert duplicate names`
	"""
	homer = kb_inmemory.get_resource_by_urn("urn:cts:greekLit:tlg0012")
	lang = "it"
	name = "Omero"
	number_names_before = len(homer.get_names())
	assert (lang, name) in homer.get_names()
	assert homer.add_name(name, lang) is False
	number_names_after = len(homer.get_names())
	assert number_names_before == number_names_after
def test_hucitauthor_add_abbreviation(kb_inmemory):
	abbr = "Arist."
	aristophanes = kb_inmemory.get_resource_by_urn("urn:cts:greekLit:tlg0019")
	aristophanes.add_abbreviation(abbr)
	aristophanes.load()
	assert abbr in aristophanes.get_abbreviations()
def test_hucitauthor_set_urn(kb_inmemory):
	homer = kb_inmemory.get_resource_by_urn("urn:cts:greekLit:tlg0012")
	new_urn = "urn:cts:greekLit:tlg0013"
	homer.set_urn(new_urn)
	assert str(homer.get_urn()) == new_urn
# TESTS FOR HUCITWORK
def test_hucitwork_set_urn(kb_inmemory):
	iliad = kb_inmemory.get_resource_by_urn("urn:cts:greekLit:tlg0012.tlg001")
	new_urn = "urn:cts:greekLit:tlg0012.iliad"
	iliad.set_urn(new_urn)
	assert str(iliad.get_urn()) == new_urn
def test_hucitwork_to_json(kb_inmemory):
	"""
	Test for `HucitAuthor.to_json()`.
	"""
	odyssey = kb_inmemory.get_resource_by_urn("urn:cts:greekLit:tlg0012.tlg002")
	json_string = odyssey.to_json()
	logger.info(json_string)
def test_hucitwork_add_abbreviation(kb_inmemory):
	odyssey = kb_inmemory.get_resource_by_urn("urn:cts:greekLit:tlg0012.tlg002")
	assert odyssey.add_abbreviation("Od.") is False
	assert odyssey.add_abbreviation("Odyss.") is True
def test_hucitwork_get_abbreviations(kb_inmemory):
	iperide = kb_inmemory.get_resource_by_urn("urn:cts:greekLit:tlg0030")
	combined_abbreviations = iperide.get_works()[0].get_abbreviations(combine=True)
	assert combined_abbreviations is not None and type(combined_abbreviations) is type([])
	logger.info(combined_abbreviations)