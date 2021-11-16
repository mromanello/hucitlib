#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com

import os

# import ipdb

try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import surf
import json
import logging
from surf.resource import Resource
from hucitlib.surfext import *
from pyCTS import CTS_URN
from typing import Optional, Dict, List, Tuple
import pkg_resources
import hucitlib.__version__
from hucitlib.exceptions import ResourceNotFound
from retrying import retry
from rdflib import Literal, URIRef
from tqdm import tqdm

# from multiprocessing import Pool
from collections import ChainMap

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_FILENAME = "druid.ini"


def get_abbreviations(kb):
    """
    For the sake of profiling.
    """
    return {
        "%s$$n%i" % (author.get_urn(), i): abbrev
        for author in kb.get_authors()
        for i, abbrev in enumerate(author.get_abbreviations())
        if author.get_urn() is not None
    }


class KnowledgeBase(object):
    """
    ``KnowledgeBase`` is a class that allows for accessing a HuCit
    knowledge base in an object-oriented fashion. The abstraction layer it provides
    means that you can use, search and modify its content without having to worry about
    the underlying modelling of data in RDF.
    """

    def _register_mappings(self):
        self._session.mapping[surf.ns.EFRBROO.F10_Person] = HucitAuthor
        self._session.mapping[surf.ns.EFRBROO.F1_Work] = HucitWork
        self._session.mapping[surf.ns.HUCIT.TextStructure] = HucitTextStructure
        self._session.mapping[surf.ns.HUCIT.TextElement] = HucitTextElement
        return

    def _register_namespaces(self):
        surf.ns.register(ecrm="http://erlangen-crm.org/current/")
        surf.ns.register(efrbroo="http://erlangen-crm.org/efrbroo/")
        surf.ns.register(hucit="http://purl.org/net/hucit#")
        return

    def __init__(self, config_file: str = None) -> None:
        """
        :param str config_file: Path to the configuration file containing the
            parameters to connect to the triple store whose data will be accessible
            via the ``KnowledgeBase`` object.
        :return: Description of returned object.
        :rtype: None

        .. note::
            By default (i.e. when no configuration file is specified) a new
            ``KnowledgeBase`` instance will be created that reads data directly
            from the triple store hosted at `Druid <https://druid.datalegend.net/mromanello/hucit/>`_.
            **NB**: please note that all methods that *modify* entries in the KB won't work as that
            triple store is *read-only*.

        Example of usage:

        .. code-block:: python

            >>> from hucit_kb import KnowledgeBase
            >>> kb = KnowledgeBase()
            >>> homer = kb.get_resource_by_urn('urn:cts:greekLit:tlg0012')
            >>> print(homer.rdfs_label.one)

        """
        self._author_names = None
        self._work_titles = None
        self._author_abbreviations = None
        self._work_abbreviations = None

        if config_file is None:
            config_file = pkg_resources.resource_filename(
                "hucitlib", f"config/{DEFAULT_CONFIG_FILENAME}"
            )

        try:
            config = configparser.ConfigParser()
            config.read_file(open(config_file))
            self._store_params = dict(config.items("surf"))
            if "port" in self._store_params:
                self._store_params["port"] = int(
                    self._store_params["port"]
                )  # force the `port` to be an integer
            self._store = surf.Store(**self._store_params)
            self._session = surf.Session(self._store, {})
            if "rdflib_store" in self._store_params:
                basedir = pkg_resources.resource_filename("knowledge_base", "data/kb/")
                sources = [
                    "%s%s" % (basedir, file)
                    for file in self._store_params["knowledge_base_sources"].split(",")
                ]
                source_format = self._store_params["sources_format"]
                for source_path in sources:
                    self._store.writer._graph.parse(
                        source=source_path, format=source_format
                    )
                    logger.info(
                        "The KnowledgeBase contains %i triples" % self._store.size()
                    )
            self._register_namespaces()
            self._register_mappings()
        except Exception as e:
            raise e

    def __getstate__(self):
        """
        Instances of `surfrdf.Store` and `surfrdf.Session` cannot be serialised.
        Thus they need to be dropped when pickling.
        """
        odict = self.__dict__.copy()
        del odict["_store"]
        del odict["_session"]
        return odict

    def __setstate__(self, dict):
        self.__dict__.update(dict)
        self._store = surf.Store(**self._store_params)
        self._session = surf.Session(self._store, {})
        # don't forget to reload the triples if it's an in-memory store!
        if "rdflib_store" in self._store_params:
            basedir = pkg_resources.resource_filename("knowledge_base", "data/kb/")
            sources = [
                "%s%s" % (basedir, file)
                for file in self._store_params["knowledge_base_sources"].split(",")
            ]
            source_format = self._store_params["sources_format"]
            for source_path in sources:
                self._store.writer._graph.parse(
                    source=source_path, format=source_format
                )
                logger.info(
                    "The KnowledgeBase contains %i triples" % self._store.size()
                )
        self._register_namespaces()
        self._register_mappings()

    @property
    def settings(self) -> Dict[str, str]:
        return self._store_params

    # some legacy methods
    @property
    def author_names(self) -> Dict[str, str]:
        """
        Returns a dictionary like this:

        .. code-block:: python

            {
                "urn:cts:greekLit:tlg0012$$n1" : "Homer"
                , "urn:cts:greekLit:tlg0012$$n2" : "Omero"
                , ...
            }
        """

        def fetch_names(author):
            return {
                "%s$$n%i" % (author.get_urn(), i): name[1]
                for i, name in enumerate(author.get_names())
            }

        if self._author_names is None:
            authors = self.get_authors()
            author_names = [
                fetch_names(author)
                for author in tqdm(authors)
                if author.get_urn() is not None
            ]
            self._author_names = dict(ChainMap(*author_names))

        return self._author_names

    @property
    def author_abbreviations(self):
        return {
            "%s$$n%i" % (author.get_urn(), i): abbrev
            for author in self.get_authors()
            for i, abbrev in enumerate(author.get_abbreviations())
            if author.get_urn() is not None
        }

    @property
    def work_titles(self):
        return {
            "%s$$n%i" % (work.get_urn(), i): title[1]
            for author in self.get_authors()
            for work in author.get_works()
            for i, title in enumerate(work.get_titles())
            if work.get_urn() is not None
        }

    @property
    def work_abbreviations(self):
        return {
            "%s$$n%i" % (work.get_urn(), i): abbrev
            for author in self.get_authors()
            for work in author.get_works()
            for i, abbrev in enumerate(
                work.get_abbreviations(combine=False)
                + work.get_abbreviations(combine=True)
            )
        }

    @retry(stop_max_attempt_number=5, wait_fixed=5000)
    def get_resource_by_urn(self, urn):
        """Fetch the resource corresponding to the input CTS URN.

        Currently supports
        only HucitAuthor and HucitWork.

        :param urn: the CTS URN of the resource to fetch
        :return: either an instance of `HucitAuthor` or of `HucitWork`

        """
        search_query = (
            """
            PREFIX frbroo: <http://erlangen-crm.org/efrbroo/>
            PREFIX crm: <http://erlangen-crm.org/current/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?resource_URI

            WHERE {
                ?resource_URI crm:P1_is_identified_by ?urn .
                ?urn a crm:E42_Identifier .
                ?urn rdfs:label "%s"
            }
        """
            % urn
        )
        # check type of the input URN
        try:
            assert isinstance(urn, CTS_URN)
        except Exception as e:
            # convert to pyCTS.CTS_URN if it's a string
            urn = CTS_URN(urn)
            logger.debug("Converted the input urn from string to %s" % type(CTS_URN))

        # determine the type of returned resource based on CTS URN semantics
        if urn.passage_component is not None:
            resource_type = self._session.get_class(surf.ns.HUCIT["TextElement"])
        elif urn.work is not None:
            resource_type = self._session.get_class(surf.ns.EFRBROO["F1_Work"])
        elif (
            urn.work is None
            and urn.textgroup is not None
            and urn.passage_component is None
        ):
            resource_type = self._session.get_class(surf.ns.EFRBROO["F10_Person"])

        # execute the sparql query and return the result
        result = self._store.execute_sparql(search_query)
        if len(result["results"]["bindings"]) == 0:
            raise ResourceNotFound
        else:
            tmp = result["results"]["bindings"][0]
            resource_uri = tmp["resource_URI"]["value"]
            return self._session.get_resource(resource_uri, resource_type)

    # TODO: if the underlying store is not Virtuoso it should fail
    # and say something useful ;-)
    def search(self, search_string: str) -> List[Tuple[str, Resource]]:
        """Searches for a given string through the resources' labels.

        :param str search_string: Description of parameter `search_string`.
        :return: Description of returned object.
        :rtype: List[Tuple[str, Resource]]

        """
        query = (
            """
        SELECT ?s ?label ?type
        WHERE {
            ?s a ?type .
            ?s rdfs:label ?label .
            ?label bif:contains "'%s'" .
        }
        """
            % search_string
        )
        response = self._session.default_store.execute_sparql(query)
        results = [
            (result["s"]["value"], result["label"]["value"], result["type"]["value"])
            for result in response["results"]["bindings"]
        ]
        resources = [
            (label, self._session.get_resource(subject, self._session.get_class(type)))
            for subject, label, type in results
        ]

        Name = self._session.get_class(surf.ns.EFRBROO["F12_Name"])
        Title = self._session.get_class(surf.ns.EFRBROO["E35_Title"])
        Work = self._session.get_class(surf.ns.EFRBROO["F1_Work"])
        Person = self._session.get_class(surf.ns.EFRBROO["F10_Person"])

        result = []
        for label, resource in resources:
            if resource.uri == surf.ns.EFRBROO["E35_Title"]:
                work = Work.get_by(efrbroo_P102_has_title=resource).first()
                result.append((label, work))
            elif resource.uri == surf.ns.EFRBROO["F12_Name"]:
                author = Person.get_by(ecrm_P1_is_identified_by=resource).first()
                result.append((label, author))
            elif resource.uri == surf.ns.ECRM["E41_Appellation"]:
                try:
                    name = Name.get_by(ecrm_P139_has_alternative_form=resource).first()
                    assert name is not None
                    author = Person.get_by(ecrm_P1_is_identified_by=name).first()
                    result.append((label, author))
                except Exception as e:
                    title = Title.get_by(
                        ecrm_P139_has_alternative_form=resource
                    ).first()
                    assert title is not None
                    work = Work.get_by(efrbroo_P102_has_title=title).first()
                    result.append((label, work))
        return result

    def get_authors(self) -> List[HucitAuthor]:
        """Lists all authors contained in the knowledge base.

        :return: A list of authors.
        :rtype: List[HucitAuthor]

        """
        Person = self._session.get_class(surf.ns.EFRBROO["F10_Person"])
        return list(Person.all())

    def get_works(self):
        """Return the author's works.

        :return: a list of `HucitWork` instances.

        """
        Work = self._session.get_class(surf.ns.EFRBROO["F1_Work"])
        return list(Work.all())

    def get_author_label(self, urn):
        """Get the label corresponding to the author identified by the CTS URN.

        try to get an lang=en label (if multiple labels in this lang pick the shortest)
        try to get a lang=la label (if multiple labels in this lang exist pick the shortest)
        try to get a lang=None label (if multiple labels in this lang exist pick the shortest)

        returns None if no name is found

        """
        author = self.get_resource_by_urn(urn)
        names = author.get_names()
        en_names = sorted([name[1] for name in names if name[0] == "en"], key=len)
        try:
            assert len(en_names) > 0
            return en_names[0]
        except Exception as e:
            none_names = sorted([name[1] for name in names if name[0] == None], key=len)
            try:
                return none_names[0]
            except Exception as e:
                la_names = sorted(
                    [name[1] for name in names if name[0] == "la"], key=len
                )
                try:
                    assert len(la_names) > 0
                    return la_names[0]
                except Exception as e:
                    return None

    def get_work_label(self, urn):
        """

        Get the label corresponding to the work identified
        by the input CTS URN.

        try to get an lang=en label
        try to get a lang=la label
        try to get a lang=None label

        returns None if no title is found

        """
        work = self.get_resource_by_urn(urn)
        titles = work.get_titles()
        en_titles = [title[1] for title in titles if title[0] == "en"]
        try:
            assert len(en_titles) > 0
            return en_titles[0]
        except Exception as e:
            la_titles = [title[1] for title in titles if title[0] == None]
            try:
                assert len(la_titles) > 0
                return la_titles[0]
            except Exception as e:
                none_titles = [title[1] for title in titles if title[0] == "la"]
                try:
                    return none_titles[0]
                except Exception as e:
                    return None

    # TODO: re-implement
    def get_statistics(self) -> Dict[str, int]:
        """
        Gather basic stats about the Knowledge Base and its contents.

        .. note::

            This method currently has some performances issues.

        :return: a dictionary

        """
        statistics = {
            "number_authors": 0,
            "number_author_names": 0,
            "number_author_abbreviations": 0,
            "number_works": 0,
            "number_work_titles": 0,
            "number_title_abbreviations": 0,
            "number_opus_maximum": 0,
        }
        for author in self.get_authors():
            if author.get_urn() is not None:
                opmax = (
                    True
                    if self.get_opus_maximum_of(author.get_urn()) is not None
                    else False
                )
                if opmax:
                    statistics["number_opus_maximum"] += 1
            statistics["number_authors"] += 1
            statistics["number_author_names"] += len(author.get_names())
            statistics["number_author_abbreviations"] += len(author.get_abbreviations())
            for work in author.get_works():
                statistics["number_works"] += 1
                statistics["number_work_titles"] += len(work.get_titles())
                statistics["number_title_abbreviations"] += len(
                    work.get_abbreviations()
                )
        return statistics

    def get_opus_maximum_of(self, author_cts_urn):
        """Return the author's opux maximum (None otherwise).

        Given the CTS URN of an author, this method returns its opus maximum.
        If not available returns None.

        :param author_cts_urn: the author's CTS URN.
        :return: an instance of `surfext.HucitWork` or None

        """
        author = self.get_resource_by_urn(author_cts_urn)
        assert author is not None
        works = author.get_works()

        if len(works) > 1:
            for work in works:
                if work.is_opus_maximum():
                    return work
        elif len(works) == 1:
            return works[0]
        else:
            return None

    # is this method really needed?
    def get_textelement_types(self) -> List[surf.resource.Resource]:
        """Returns all TextElementTypes defined in the knowledge base.

        :return: Description of returned object.
        :rtype: List[surf.resource.Resource]

        """
        E55_Type = self._session.get_class(surf.ns.ECRM["E55_Type"])
        return E55_Type.all()

    def get_textelement_type(self, label: str) -> Optional[surf.resource.Resource]:
        """Returns a TextElementType (instance of E55_Type) if present.

        .. note::
            ``label`` (lowercased) is used to create the URI
            (http://purl.org/hucit/kb/types/{label}).

        :param str label: Description of parameter `label`.
        :return: Description of returned object.
        :rtype: surf.resource.Resource

        """
        E55_Type = self._session.get_class(surf.ns.ECRM["E55_Type"])

        # URI of expected text element type
        textelement_type = E55_Type(
            os.path.join("http://purl.org/hucit/kb/types/", label.lower())
        )
        if textelement_type.is_present():
            return textelement_type
        else:
            return None

    def add_textelement_type(
        self, label: str, lang: str = "en"
    ) -> Optional[surf.resource.Resource]:
        """Adds a new TextElementType to the Knowledge base if not yet present.

        :param str label: Description of parameter `label`.
        :param str lang: Description of parameter `lang`.
        :return: Description of returned object.
        :rtype: Optional[surf.resource.Resource]

        .. code-block:: python

            # this will work only when connecting to a triples store
            # where you have access in writing mode
            >>> from hucit_kb import KnowledgeBase
            >>> kb = KnowledgeBase()
            >>> element_type_obj = kb.add_textelement_type("book")

        """
        label = label.lower()
        E55_Type = self._session.get_class(surf.ns.ECRM["E55_Type"])

        # try to see if it exists, otherwise create it
        if self.get_textelement_type(label) is None:
            new_E55_type = E55_Type(
                os.path.join("http://purl.org/hucit/kb/types/", label)
            )
            new_E55_type.rdfs_label.append(Literal(label, lang))
            new_E55_type.save()
            return new_E55_type
        else:
            return None

    def add_textelement_types(self, types: List[str]) -> None:
        """Adds the text element type in case it doesn't exist.

        :param List[str] types: a list of strings (e.g. ["book", "poem", "line"])
        :return: Description of returned object.
        :rtype: None

        .. code-block:: python

            # this will work only when connecting to a triples store
            # where you have access in writing mode
            >>> from hucit_kb import KnowledgeBase
            >>> kb = KnowledgeBase()
            >>> kb.add_textelement_types(["book", "line"])

        """

        for el_type in types:
            el_type_obj = self.get_textelement_type(el_type)
            if el_type_obj is None:
                new_el_obj = self.add_textelement_type(el_type)
                print(
                    f"Added new text element type: {new_el_obj.subject}",
                    f" {new_el_obj.rdfs_label}",
                )
            else:
                print(f"Level {el_type} already exists: {el_type_obj.subject}")
        return

    def to_json(self):
        """
        Serialises the content of the KnowledgeBase as JSON.

        :return: TODO
        """
        return json.dumps(
            {
                "statistics": self.get_statistics(),
                "authors": [
                    json.loads(author.to_json()) for author in self.get_authors()
                ],
            },
            indent=2,
        )

    #####################
    # Factory methods   #
    #####################

    @retry(stop_max_attempt_number=5, wait_fixed=5000)
    def create_text_element(
        self,
        work: surf.resource.Resource,
        urn_string: str,
        element_type: surf.resource.Resource,
        source_uri: str = None,
    ):
        """Short summary.

        :param str urn: Text element's URN.
        :param surf.resource.Resource element_type: Text element type.
        :return: The newly created text element.
        :rtype: type

        .. code-block:: python

            >>> iliad = kb.get_resource_by_urn("urn:cts:greekLit:tlg0012.tlg001")
            >>> etype_book = kb.get_textelement_type("book")
            >>> ts = iliad.structure
            >>> ts.create_element(
                "urn:cts:greekLit:tlg0012.tlg001:1",
                element_type=type_book,
                following_urn="urn:cts:greekLit:tlg0012.tlg001:2"
            )
        """
        urn = CTS_URN(urn_string)
        work_label = str(work.rdfs_label.one).split(" :: ")[0]
        type_label = str(element_type.rdfs_label.one)
        element_label = f"{work_label} {type_label} {urn.passage_component}"

        # mint the URI
        element_uri = os.path.join(work.subject, urn.passage_component)
        TextElement = self._session.get_class(surf.ns.HUCIT["TextElement"])
        new_element = TextElement(element_uri)
        new_element.ecrm_P2_has_type = element_type
        new_element.rdfs_label = [element_label]

        if source_uri:
            new_element.hucit_resolves_to = URIRef(source_uri)

        new_element.save()

        # create an RDF representation of the CTS URN
        # identifying this textual element
        element_urn = self.create_cts_urn(new_element, urn_string)

        # perhaps send it to the logger instead
        logger.info(
            f"Created text element {new_element.subject} => {repr(new_element)}"
        )
        return new_element

    def create_cts_urn(
        self, resource: surf.resource.Resource, urn_string: str
    ) -> Optional[surf.resource.Resource]:
        """Creates a CTS URN object and assigns it to a given resource.

        :param surf.resource.Resource resource: KB entry to be identified by the
            CTS URN.
        :param str urn_string: CTS URN identifier (e.g. ``urn:cts:greekLit:tlg0012``)
        :return: The newly created object or ``None`` if it already existed.
        :rtype: Optional[surf.resource.Resource]

        """
        Type = self._session.get_class(surf.ns.ECRM["E55_Type"])
        Identifier = self._session.get_class(surf.ns.ECRM["E42_Identifier"])
        id_uri = os.path.join(resource.subject, "cts_urn")
        id = Identifier(id_uri)
        if id.is_present():
            logger.info(
                "Identifier not created!"
                f"{resource.subject} already has a CTS URN identifier: {id.subject}"
            )
        else:
            id.rdfs_label = Literal(urn_string)
            id.ecrm_P2_has_type = Type(BASE_URI_TYPES % "CTS_URN")
            id.save()
        resource.ecrm_P1_is_identified_by = id
        resource.update()
        return id
