#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com

"""Command line interface for a HuCit knowledge base.

Usage:
    knowledge_base/cli.py find <search_string>
    knowledge_base/cli.py add (name|abbr|title|sameas) --to=<cts_urn> <string_to_add> [--config-file=<path>]
    knowledge_base/cli.py (-h | --help)

Options:
    --to=<cts_urn> CTS URN of the author/work to edit.
    --config-file=<path> Path to the configuration file (overwrites default configuration).

"""
#knowledge_base/cli.py find “urn:cts:greekLit:tlg0012"
#knowledge_base/cli.py add —-what=[name|abbr|title|sameas] —-to=“urn:cts:greekLit:tlg0012” “Omero@it"

from __future__ import print_function
from __future__ import unicode_literals

import logging
from pyCTS import CTS_URN, BadCtsUrnSyntax
import surf
from surfext import *
from docopt import docopt
from __init__ import KnowledgeBase
from surf.plugin.sparql_protocol.reader import SparqlReaderException


logger = logging.getLogger('KnowledgeBase_CLI')

def print_results(matches):
    """
    :param matche: a list of tuples.
    """
    output = ""
    for n, match in enumerate(matches):
        matched_text = match[0][:40]+"..." if len(match[0]) > 40 else match[0]
        search_result = match[1]
        if search_result.uri==surf.ns.EFRBROO['F10_Person']:
            label = unicode(search_result)[:40]+"..." if len(unicode(search_result)) > 40 else unicode(search_result)
            print("\n{:5}) {:50} {:40} (Matched: \"{}\")\n".format(n+1, label, search_result.get_urn(), matched_text))
        elif search_result.uri==surf.ns.EFRBROO['F1_Work']:
            label = "{}, {}".format(search_result.author, search_result) 
            label = label[:40]+"..." if len(label) > 40 else label
            print("\n{:5}) {:50} {:40} (Matched: \"{}\")\n".format(n+1, label, search_result.get_urn(), matched_text))

def show_result(resource, verbose=False):
    """
    TODO
    """
    if resource.uri==surf.ns.EFRBROO['F10_Person']:
        print("\n{} ({})\n".format(unicode(resource), resource.get_urn()))
        works = resource.get_works()
        print("Works by {} ({}):\n".format(resource, len(works)))
        [show_result(work) for work in works]
        print("\n")
    elif resource.uri==surf.ns.EFRBROO['F1_Work']:
        if verbose:
            print("\n{} ({})".format(unicode(resource), resource.get_urn()))
            print("\nTitles:")
            print("\n".join(["{:20} ({})".format(title, lang) for lang, title in resource.get_titles()]))
            if len(resource.get_abbreviations()) > 0:
                print("\nAbbreviations: {}\n".format(", ".join(["{}".format(abbr) for abbr in resource.get_abbreviations()])))
        else:
            print("{:50} {:40}".format(unicode(resource), resource.get_urn()))


def main(arguments):
    """
    Define the CLI inteface/commands.
    """
    kb = KnowledgeBase("knowledge_base/config/virtuoso.ini")
    #print(arguments)
    if arguments["find"]:
        search_string = arguments["<search_string>"]
        try:
            urn = CTS_URN(search_string)
            match = kb.get_resource_by_urn(str(urn))
            show_result(match, verbose=True)
            return
        except BadCtsUrnSyntax as e:
            pass
        except IndexError as e:
            raise e
            print("\nNo records with this CTS URN!\n")
            return
        try:
            matches = kb.search(search_string)
            print("\nSearching for \"%s\" yielded %s results" % (search_string, len(matches)))
            print_results(matches)
            return
        except SparqlReaderException as e:
            print("\nWildcard word needs at least 4 leading characters")
    elif arguments["add"]:
        pass

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')
    main(arguments)