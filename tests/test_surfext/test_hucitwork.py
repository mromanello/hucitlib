# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com
import logging
import pytest
import pdb
import json

logger = logging.getLogger(__name__)

########################
# TESTS FOR HucitWork  #
########################

@pytest.mark.run(order=12)
def test_hucitwork_set_urn(kb_virtuoso):
    urn = "urn:cts:greekLit:tlg0012.tlg001"
    iliad = kb_virtuoso.get_resource_by_urn(urn)
    new_urn = "urn:cts:greekLit:tlg0012.iliad"
    iliad.set_urn(new_urn)
    iliad.load()
    assert str(iliad.get_urn()).value == new_urn

    iliad = kb_virtuoso.get_resource_by_urn(new_urn)
    iliad.set_urn(urn)
    iliad.load()
    assert str(iliad.get_urn()).value == urn


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
