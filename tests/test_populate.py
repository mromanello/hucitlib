# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com
import logging
import pytest
import pkg_resources
from conftest import OUTPUT_DIR
from hucitlib.populate import populate_text_structure
from hucitlib.populate import download_text_structure, load_text_structure_JSON


logger = logging.getLogger(__name__)

def test_download_text_structure():
    work = "urn:cts:greekLit:tlg0011.tlg003"
    max_n_text_elements = 10

    download_text_structure(work, basedir=OUTPUT_DIR, sample_size=max_n_text_elements)
    text_structure_json = load_text_structure_JSON(work, OUTPUT_DIR)

    retrieved_element_n = 0
    for level_n, level_label in text_structure_json['levels']:
        retrieved_element_n += len(text_structure_json['valid_reffs'][str(level_n)])

    assert retrieved_element_n == max_n_text_elements

def test_populate_text_structure(kb_virtuoso):
    work_urn = "urn:cts:greekLit:tlg0011.tlg003"
    work_obj = kb_virtuoso.get_resource_by_urn(work_urn)
    text_structure_json = load_text_structure_JSON(work_urn, OUTPUT_DIR)
    populate_text_structure(kb_virtuoso, work_obj, text_structure_json)
