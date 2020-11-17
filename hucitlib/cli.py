#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com

"""Command line interface for a HuCit knowledge base.

Usage:
    hucit find <search_string> [--config-file=<path>]
    hucit add (name|abbr|title|sameas) --to=<cts_urn> <string_to_add> [--config-file=<path>]
    hucit (-h | --help)

Options:
    --to=<cts_urn> CTS URN of the author/work to edit.
    --config-file=<path> Path to the configuration file (overwrites default configuration).

"""

from __future__ import print_function, unicode_literals

import logging

import pkg_resources
import surf
from typing import List, Tuple
from docopt import docopt
from pyCTS import CTS_URN, BadCtsUrnSyntax
from surf.plugin.sparql_protocol.reader import SparqlReaderException

from hucitlib import KnowledgeBase
from hucitlib.exceptions import ResourceNotFound
from hucitlib.surfext import *

logger = logging.getLogger("KnowledgeBase_CLI")


def print_results(matches: Tuple[str, surf.resource.Resource]) -> None:
    """Prints to stdout the list of search results.

    :param Tuple[str, surf.resource.Resource] matches: List of search results, where
        each result is a tuple containing the matching text and the object
        (``surf.resource.Resource``).
    :rtype: None

    """
    for n, match in enumerate(matches):
        matched_text = match[0][:40] + "..." if len(match[0]) > 40 else match[0]
        search_result = match[1]
        if search_result.uri == surf.ns.EFRBROO["F10_Person"]:
            label, urn = search_result.rdfs_label.first.split(" :: ")
            label = label[:40] + "..." if len(label) > 40 else label
            print(f"\n{n+1:5}) {urn} {label:50} (Matched: '{matched_text}')\n")
        elif search_result.uri == surf.ns.EFRBROO["F1_Work"]:
            work_label, urn = search_result.rdfs_label.first.split(" :: ")
            label = work_label[:40] + "..." if len(work_label) > 40 else work_label
            print(f'\n{n + 1:5}) {label:50} {urn} (Matched: "{matched_text}")\n')
    return


def print_abbreviations(abbreviations: List[str]) -> None:
    pass


def print_labels(labels: List[str]) -> None:
    pass


def display_resource(resource: surf.resource.Resource, verbose: bool = False) -> None:
    """Prints to stdout informations about a given KB entry.

    :param surf.resource.Resource resource: Description of parameter `resource`.
    :param bool verbose: Description of parameter `verbose`.
    :return: Description of returned object.
    :rtype: None

    """
    if resource.uri == surf.ns.EFRBROO["F10_Person"]:
        print(f"\n{resource.rdfs_label.first} ({resource.subject}) \n")
        works = resource.get_works()
        print(f"{len(works)} works by this author:")
        [display_resource(work) for work in works]
        print("\n")
        sameas_links = "\n".join([f" - {link}" for link in resource.owl_sameAs])
        print(f"Related resources:\n{sameas_links}")
    elif resource.uri == surf.ns.EFRBROO["F1_Work"]:
        if verbose:
            print(f"\n{resource.rdfs_label.first}")
            print("\nTitles:")
            print(
                "\n".join(
                    [
                        "{:20} ({})".format(title, lang)
                        for lang, title in resource.get_titles()
                    ]
                )
            )
            if len(resource.get_abbreviations()) > 0:
                print(
                    "\nAbbreviations: {}\n".format(
                        ", ".join(
                            ["{}".format(abbr) for abbr in resource.get_abbreviations()]
                        )
                    )
                )
            sameas_links = "\n".join([f" - {link}" for link in resource.owl_sameAs])
            print(f"Related resources:\n{sameas_links}")
        else:
            print(f" - {resource.rdfs_label.first:80} ({resource.subject})")


def main():
    """Define the CLI inteface/commands."""
    arguments = docopt(__doc__)
    if arguments["--config-file"] is not None:
        cfg_filename = arguments["--config-file"]
    else:
        cfg_filename = pkg_resources.resource_filename(
            "hucitlib", "config/virtuoso.ini"
        )
    kb = KnowledgeBase(cfg_filename)

    # the user has issued a `find` command
    if arguments["find"]:
        search_string = arguments["<search_string>"]
        try:
            urn = CTS_URN(search_string)
            match = kb.get_resource_by_urn(str(urn))
            display_resource(match, verbose=True)
            return
        except BadCtsUrnSyntax as e:
            pass
        except IndexError as e:
            raise e
            print("\nNo records with this CTS URN!\n")
            return
        try:
            matches = kb.search(search_string)
            print(
                '\nSearching for "%s" yielded %s results'
                % (search_string, len(matches))
            )
            print_results(matches)
            return
        except SparqlReaderException as e:
            print("\nWildcard word needs at least 4 leading characters")
    # the user has issued an `add` command
    elif arguments["add"]:
        input_urn = arguments["--to"]

        # first let's check if it's a valid URN
        try:
            urn = CTS_URN(input_urn)
        except Exception as e:
            print("The provided URN ({}) is invalid!".format(input_urn))
            return

        try:
            resource = kb.get_resource_by_urn(urn)
            assert resource is not None
        except ResourceNotFound:
            print("The KB does not contain a resource identified by {}".format(urn))
            return

        print(arguments)
        # if arguments[""]
        pass


if __name__ == "__main__":
    main()
