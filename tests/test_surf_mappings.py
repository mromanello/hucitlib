# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com
import logging
import pytest
import pdb
import json

logger = logging.getLogger(__name__)


# TESTS FOR HUCITAUTHOR
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
    new_urn = "urn:cts:greekLit:tlg0013"
    homer.set_urn(new_urn)
    assert str(homer.get_urn()) == new_urn

    homer = kb_virtuoso.get_resource_by_urn(new_urn)
    homer.set_urn(urn)
    assert str(homer.get_urn()) == urn


# TESTS FOR HUCITWORK
@pytest.mark.run(order=12)
def test_hucitwork_set_urn(kb_virtuoso):
    urn = "urn:cts:greekLit:tlg0012.tlg001"
    iliad = kb_virtuoso.get_resource_by_urn(urn)
    new_urn = "urn:cts:greekLit:tlg0012.iliad"
    iliad.set_urn(new_urn)
    assert str(iliad.get_urn()) == new_urn

    iliad = kb_virtuoso.get_resource_by_urn(new_urn)
    iliad.set_urn(urn)
    assert str(iliad.get_urn()) == urn


@pytest.mark.run(order=13)
def test_hucitwork_to_json(kb_virtuoso):
    """
    Test for `HucitAuthor.to_json()`.
    """
    odyssey = kb_virtuoso.get_resource_by_urn("urn:cts:greekLit:tlg0012.tlg002")
    json_string = odyssey.to_json()
    logger.info(json_string)


@pytest.mark.run(order=14)
def test_hucitwork_add_abbreviation(kb_virtuoso):
    odyssey = kb_virtuoso.get_resource_by_urn("urn:cts:greekLit:tlg0012.tlg002")
    assert odyssey.add_abbreviation("Od.") is False
    assert odyssey.add_abbreviation("Odyss.") is False


@pytest.mark.run(order=15)
def test_hucitwork_get_abbreviations(kb_virtuoso):
    iperide = kb_virtuoso.get_resource_by_urn("urn:cts:greekLit:tlg0030")
    combined_abbreviations = iperide.get_works()[0].get_abbreviations(
        combine=True
    )
    assert combined_abbreviations is not None and \
        type(combined_abbreviations) is type([])
    logger.info(combined_abbreviations)


def test_hucitwork_opmax(kb_virtuoso):
    """Test opus maximum-related functions."""
    # test that AR's Argonatica are set as his OpMax
    logger.info("Veryfying AR's Argonautica")
    AR_argonautica = kb_virtuoso.get_resource_by_urn(
        "urn:cts:greekLit:tlg0001.tlg001"
    )
    AR_urn = "urn:cts:greekLit:tlg0001"
    assert AR_argonautica.is_opus_maximum() is True
    assert AR_argonautica == kb_virtuoso.get_opus_maximum_of(AR_urn)

    logger.info("Veryfying Propertius' Elegies")
    Prop_elegies = kb_virtuoso.get_resource_by_urn(
        "urn:cts:latinLit:phi0620.phi001"
    )
    assert Prop_elegies.is_opus_maximum() is True


def test_hucitwork_add_title(kb_virtuoso):
    in_gildonem = kb_virtuoso.get_resource_by_urn('urn:cts:cwkb:1362.4399')
    in_gildonem.add_title('Bellum Gildonicum', lang='la')
