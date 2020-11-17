# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com
import logging
import pytest
import pdb
import json

logger = logging.getLogger(__name__)

###########################
# TESTS FOR HucitAuthor   #
###########################

@pytest.mark.run(order=8)
def test_hucitauthor_to_json(kb_virtuoso):
    """
    Test for `HucitAuthor.to_json()`.
    """
    homer = kb_virtuoso.get_resource_by_urn("urn:cts:greekLit:tlg0012")
    json_string = homer.to_json()
    logger.info(json_string)
    dict_from_json = json.loads(json_string)
    assert dict_from_json is not None and json_string is not None


@pytest.mark.run(order=9)
def test_hucitauthor_add_duplicate_name(kb_virtuoso):
    """
    Test to ensure that `HucitAuthor.add_name(...) does not insert duplicate names`
    """
    homer = kb_virtuoso.get_resource_by_urn("urn:cts:greekLit:tlg0012")
    lang = "it"
    name = "Omero"
    number_names_before = len(homer.get_names())
    assert (lang, name) in homer.get_names()
    assert homer.add_name(name, lang) is False
    number_names_after = len(homer.get_names())
    assert number_names_before == number_names_after


@pytest.mark.run(order=10)
def test_hucitauthor_add_abbreviation(kb_virtuoso):
    """
    TODO: try adding abbreviation to an author that does not have any
    """
    abbr = "Arist."
    aristophanes = kb_virtuoso.get_resource_by_urn("urn:cts:greekLit:tlg0019")
    aristophanes.add_abbreviation(abbr)
    aristophanes.load()
    assert abbr in aristophanes.get_abbreviations()


@pytest.mark.run(order=11)
def test_hucitauthor_set_urn(kb_virtuoso):
    urn = "urn:cts:greekLit:tlg0012"
    homer = kb_virtuoso.get_resource_by_urn(urn)
    new_urn = "urn:cts:greekLit:homer"
    homer.set_urn(new_urn)
    homer.load()
    assert str(homer.get_urn()).value == new_urn

    homer = kb_virtuoso.get_resource_by_urn(new_urn)
    homer.set_urn(urn)
    homer.load()
    assert str(homer.get_urn()).value == urn
