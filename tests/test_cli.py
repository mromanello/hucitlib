"""Tests for the module `knowledge_base.cli`."""

# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com
import logging
import pytest
import subprocess
from conftest import DEFAULT_CONFIG_FILE

logger = logging.getLogger(__name__)


@pytest.mark.run(order=15)
def test_find_author():
    """Find the author by string search."""
    cli_output = subprocess.check_output(
        [
            "hucit",
            f"--config-file={DEFAULT_CONFIG_FILE}",
            "find",
            "Homer",
        ]
    )
    logger.info(DEFAULT_CONFIG_FILE)
    assert "urn:cts:greekLit:tlg0012" in str(cli_output)


@pytest.mark.run(order=16)
def test_find_work():
    """Find the work by string seacrh."""
    cli_output = subprocess.check_output(
        ["hucit", f"--config-file={DEFAULT_CONFIG_FILE}", "find", "Odissea"]
    )
    assert "urn:cts:greekLit:tlg0012.tlg002" in str(cli_output)


@pytest.mark.run(order=17)
def test_find_work_by_urn():
    """Find the work by CTS URN."""
    iliad_urn = "urn:cts:greekLit:tlg0012.tlg001"
    cli_output = subprocess.check_output(
        ["hucit", f"--config-file={DEFAULT_CONFIG_FILE}", "find", iliad_urn]
    )
    assert "Iliad" in str(cli_output)
