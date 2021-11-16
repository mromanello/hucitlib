#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com

"""Command line interface for populating the HuCit knowledge base.

Usage:
    hucitlib/populate.py --work=<cts_urn> --log-file=<path> --kb-config-file=<path> [--verbose]

Options:
    --work=<cts_urn>    CTS URN of the work whose citation structure should be populated
    --kb-config-file=<path> Path to the configuration file (overwrites default configuration).
    --log-file=<path>   Path to the log file
    --verbose   Turn on verbose logging

Example:
    python hucitlib/populate.py --work=urn:cts:greekLit:tlg0011.tlg004
     --log-file=hucitlib/data/tests/populate-tlg0011.tlg004.log
     --kb-config-file=hucitlib/config/virtuoso_local.ini
"""


import pkg_resources
import os
import json
import logging
from docopt import docopt
from hucitlib import init_logger
from hucitlib import KnowledgeBase
from hucitlib.exceptions import ResourceNotFound
from typing import Dict
from tqdm import tqdm
from retrying import retry
from surf.resource import Resource
from MyCapytain.resolvers.cts.api import HttpCtsResolver
from MyCapytain.retrievers.cts5 import HttpCtsRetriever

logger = logger = logging.getLogger(__name__)

TEXT_STRUCTURES_BASEDIR = pkg_resources.resource_filename(
    "hucitlib", f"data/text_structures/"
)


@retry(stop_max_attempt_number=5, wait_fixed=5000)
def fetch_textual_node(urn: str, ref: str, resolver: HttpCtsResolver):
    return resolver.getTextualNode(textId=urn, subreference=ref, prevnext=True)


def fetch_text_structure(
    urn: str, endpoint: str = "http://cts.perseids.org/api/cts", stop_at: int = -1
) -> Dict[str, object]:
    """
    Fetches the text structure of a given work from a CTS endpoint.

    :param urn: the work's CTS URN (at the work-level!,
        e.g."urn:cts:greekLit:tlg0012.tlg001")
    :type urn: string
    :param endpoint: the URL of the CTS endpoint to use (defaults to Perseids')
    :type endpoint: string
    :return: a dict with keys "urn", "provenance", "valid_reffs", "levels"
    :rtype: dict
    """

    counter = 0
    structure = {"urn": urn, "provenance": endpoint, "valid_reffs": {}}
    print(f"Retrieving text structure for {urn} from {endpoint}")

    orig_edition = None
    suffix = "grc" if "greekLit" in urn else "lat"
    resolver = HttpCtsResolver(HttpCtsRetriever(endpoint))
    work_metadata = resolver.getMetadata(urn)

    # among all editions for this work, pick the one in Greek or Latin
    try:
        orig_edition = next(
            iter(
                work_metadata.children[edition]
                for edition in work_metadata.children
                if suffix in str(work_metadata.children[edition].urn)
            )
        )
    except Exception as e:
        print(e)
        return None

    assert orig_edition is not None

    # get information about the work's citation scheme
    structure["levels"] = [
        (n + 1, level.name.lower()) for n, level in enumerate(orig_edition.citation)
    ]

    # for each hierarchical level of the text
    # fetch all citable text elements
    for level_n, level_label in structure["levels"]:
        print(f"Fetching text elements of level {level_n}")
        structure["valid_reffs"][level_n] = []

        for ref in tqdm(resolver.getReffs(urn, level=level_n)):
            element = {
                "current": "{}:{}".format(urn, ref),
            }
            if "." in ref:
                element["parent"] = "{}:{}".format(
                    urn, ".".join(ref.split(".")[: level_n - 1])
                )
            try:
                textual_node = fetch_textual_node(urn, ref, resolver)
                logging.info(
                    f"Retrieved info about {element['current']} from {endpoint}"
                )

                cts_request = f"?request=GetPassage&urn={element['current']}"
                cts_uri = f"{os.path.join(endpoint, cts_request)}"
                counter += 1

                if textual_node.nextId is not None:
                    element["following"] = "{}:{}".format(urn, textual_node.nextId)
                if textual_node.prevId is not None:
                    element["previous"] = "{}:{}".format(urn, textual_node.prevId)

                element["link"] = cts_uri
                structure["valid_reffs"][level_n].append(element)
            except Exception as e:
                logger.error(
                    f"Failed retrieving info about {element['current']} from {endpoint} with following exception: {e}"
                )
                raise (e)

            if stop_at > 0 and counter >= stop_at:
                print(f"Stopping as max value was reached ({stop_at})")
                break

        if stop_at > 0 and counter >= stop_at:
            print(f"Stopping as max value was reached ({stop_at})")
            break

    return structure


def load_text_structure_JSON(work_urn: str, basedir: str) -> Dict:
    ts_path = os.path.join(basedir, f'{work_urn.replace(":", "-")}.json')
    with open(ts_path, "r") as ifile:
        text_structure = json.load(ifile)
    return text_structure


def download_text_structure(
    urn: str, basedir: str = TEXT_STRUCTURES_BASEDIR, sample_size: int = None
) -> None:
    """

    Example:

    >>> download_text_structure('urn:cts:greekLit:tlg0012.tlg001')
    """
    if sample_size:
        text_structure = fetch_text_structure(urn, stop_at=sample_size)
    else:
        text_structure = fetch_text_structure(urn)

    path = os.path.join(basedir, "{}.json".format(urn.replace(":", "-")))
    with open(path, "w") as ofile:
        json.dump(text_structure, ofile)


def populate_text_structure(kb: KnowledgeBase, work: Resource, ts: Dict) -> None:
    """Short summary.

    :param KnowledgeBase kb: Description of parameter `kb`.
    :param Resource work: Description of parameter `work`.
    :param Dict ts: Description of parameter `ts`.
    :return: Description of returned object.
    :rtype: None

    """

    # retrieve the text structure of the work
    # if not there, create one

    work_label, work_urn = work.rdfs_label.one.split(" :: ")

    if work.has_text_structure():
        ts_obj = work.structure
    else:
        ts_obj = work.add_text_structure(
            f"Canonical text structure of {work_label}", "en"
        )

    # for each text level of a given work, iterate through all existing
    # citable text elements.
    counter = 0
    for text_level_n, element_type in ts["levels"]:
        print(
            f"Creating text elements for {work_urn}, hierarchical level {text_level_n}"
        )

        # retrieve from the KB the corresponding text element type
        # if not there, create one
        element_type_obj = kb.get_textelement_type(element_type)
        if element_type_obj is None:
            element_type_obj = kb.add_textelement_type(element_type)

        for text_element_dict in tqdm(ts["valid_reffs"][str(text_level_n)]):

            text_element_urn = text_element_dict["current"]
            try:
                element_obj = kb.get_resource_by_urn(text_element_urn)
                logger.info(
                    f"Skipping, as an element for {text_element_urn} already exists = {element_obj.subject}"
                )
                continue
            except ResourceNotFound:
                pass

            text_element = kb.create_text_element(
                work,
                text_element_urn,
                element_type_obj,
                text_element_dict["link"] if "link" in text_element_dict else None,
            )
            ts_obj.add_element(
                text_element, top_level=True if text_level_n == 1 else False
            )
            counter += 1

    # do another full pass in order to add hierarchical relations
    # between text elements
    for text_level_n, element_type in ts["levels"]:
        print(
            f"Adding relations between text elements for {work_urn}, hierarchical level {text_level_n}"
        )

        for text_element_dict in tqdm(ts["valid_reffs"][str(text_level_n)]):

            # retrieve relations between elements identified by URNs
            current_urn = text_element_dict["current"]
            following_urn = (
                text_element_dict["following"]
                if "following" in text_element_dict
                else None
            )
            previous_urn = (
                text_element_dict["previous"]
                if "previous" in text_element_dict
                else None
            )
            parent_urn = (
                text_element_dict["parent"] if "parent" in text_element_dict else None
            )

            # retrieve related text elements by their CTS URNS
            current_el = kb.get_resource_by_urn(current_urn) if current_urn else None
            following_el = (
                kb.get_resource_by_urn(following_urn) if following_urn else None
            )
            previous_el = kb.get_resource_by_urn(previous_urn) if previous_urn else None
            parent_el = kb.get_resource_by_urn(parent_urn) if parent_urn else None

            assert current_el is not None

            # TODO worth parallelising
            current_el.add_relations(
                parent=parent_el, previous=previous_el, next=following_el
            )
    return


def main():
    arguments = docopt(__doc__)
    work_id = arguments["--work"]
    log_path = arguments["--log-file"]
    kb_config = arguments["--kb-config-file"]
    verbose = True if arguments["--verbose"] else False

    # initialise the logger
    root_logger = init_logger(log_path, verbose)

    # TODO allow for an input file path to be passed as parameter
    # this file will contain a line-separated list of work CTS URNs

    """
    works = [
        "urn:cts:greekLit:tlg0011.tlg003",  # Sophocle's Ajax
        "urn:cts:greekLit:tlg0011.tlg002",  # Soph. Antigone
        "urn:cts:greekLit:tlg0011.tlg004",  # Oedipus Rex
        "urn:cts:greekLit:tlg0012.tlg001",  # Homer's Iliad
        "urn:cts:greekLit:tlg0012.tlg002",  # Homer's Odyssey
        "urn:cts:latinLit:phi0690.phi003",  # Vergil's Aeneid
        "urn:cts:greekLit:tlg0001.tlg001",  # Apollonius Rhodius' Argonautica
        "urn:cts:latinLit:phi0959.phi006",  # Ovid's Metamorphoses
    ]
    """
    works = [work_id]
    for work_urn in works:
        kb = KnowledgeBase(kb_config)
        work_obj = kb.get_resource_by_urn(work_id)

        basedir = TEXT_STRUCTURES_BASEDIR
        structure_json_path = os.path.join(
            basedir, f"{work_urn.replace(':', '-')}.json"
        )
        if os.path.exists(structure_json_path):
            print(f"Skipping {work_urn} as {structure_json_path} already exists.")
        else:
            download_text_structure(work_urn, basedir)
        ts_json = load_text_structure_JSON(work_urn, basedir)
        populate_text_structure(kb, work_obj, ts_json)


if __name__ == "__main__":
    main()
