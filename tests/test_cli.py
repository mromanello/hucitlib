# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com
import logging
import pytest
import pickle
import subprocess

logger = logging.getLogger(__name__)

@pytest.mark.run(order=15)
def test_find_author():
	cli_output = subprocess.check_output(["hucit", "find", "Homer"])
	assert "urn:cts:greekLit:tlg0012" in cli_output

@pytest.mark.run(order=16)
def test_find_work():
	cli_output = subprocess.check_output(["hucit", "find", "Odissea"])
	assert "urn:cts:greekLit:tlg0012.tlg002" in cli_output

@pytest.mark.run(order=17)
def test_find_work_by_urn():
	iliad_urn = "urn:cts:greekLit:tlg0012.tlg001"
	assert "Iliad" in subprocess.check_output(["hucit", "find", iliad_urn])