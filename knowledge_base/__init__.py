#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com

import pdb
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import surf
import json
import logging
from surfext import *
from pyCTS import CTS_URN
import pkg_resources
import __version__

logger = logging.getLogger(__name__)


def get_abbreviations(kb):
    """
    For the sake of profiling.
    """
    return {"%s$$n%i" % (author.get_urn(), i): abbrev
                for author in kb.get_authors()
                for i, abbrev in enumerate(author.get_abbreviations())
                if author.get_urn() is not None}


class ResourceNotFound(Exception):
    """Raised when the resource identified by the URN is not in the KB."""


class KnowledgeBase(object):
    """

    Example of usage:

    >>> from knowledge_base import KnowledgeBase
    >>> kb = KnowledgeBase('inmemory.ini')
    >>> print kb.get_author_label('urn:cts:greekLit:tlg0012')

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

    def __init__(self, config_file):
        """
        TODO: read default configuration file if none is provided
        """
        self._authors = None
        self._works = None
        self._author_abbreviations = None
        self._work_abbreviations = None
        try:
            config = configparser.ConfigParser()
            config.readfp(open(config_file))
            self._store_params = dict(config.items("surf"))
            if ('port' in self._store_params):
                self._store_params['port'] = int(self._store_params['port'])  # force the `port` to be an integer
            self._store = surf.Store(**self._store_params)
            self._session = surf.Session(self._store, {})
            if ('rdflib_store' in self._store_params):
                basedir = pkg_resources.resource_filename('knowledge_base', 'data/kb/')
                sources = ["%s%s" % (basedir, file) for file in self._store_params["knowledge_base_sources"].split(",")]
                source_format = self._store_params["sources_format"]
                for source_path in sources:
                    self._store.writer._graph.parse(source=source_path, format=source_format)
                    logger.info("The KnowledgeBase contains %i triples" % self._store.size())
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
        del odict['_store']
        del odict['_session']
        return odict

    def __setstate__(self, dict):
        self.__dict__.update(dict)
        self._store = surf.Store(**self._store_params)
        self._session = surf.Session(self._store, {})
        # don't forget to reload the triples if it's an in-memory store!
        if ('rdflib_store' in self._store_params):
            basedir = pkg_resources.resource_filename('knowledge_base', 'data/kb/')
            sources = ["%s%s" % (basedir, file) for file in self._store_params["knowledge_base_sources"].split(",")]
            source_format = self._store_params["sources_format"]
            for source_path in sources:
                self._store.writer._graph.parse(source=source_path, format=source_format)
                logger.info("The KnowledgeBase contains %i triples" % self._store.size())
        self._register_namespaces()
        self._register_mappings()

    # some legacy methods
    @property
    def author_names(self):
        """
        Returns a dictionary like this:

        {
            "urn:cts:greekLit:tlg0012$$n1" : "Homer"
            , "urn:cts:greekLit:tlg0012$$n2" : "Omero"
            , ...
        }
        """
        return {"%s$$n%i" % (author.get_urn(), i): name[1]
                for author in self.get_authors()
                for i, name in enumerate(author.get_names())
                if author.get_urn() is not None}

    @property
    def author_abbreviations(self):
        return {"%s$$n%i" % (author.get_urn(), i): abbrev
                for author in self.get_authors()
                for i, abbrev in enumerate(author.get_abbreviations())
                if author.get_urn() is not None}

    @property
    def work_titles(self):
        return {"%s$$n%i" % (work.get_urn(), i): title[1]
                for author in self.get_authors()
                for work in author.get_works()
                for i, title in enumerate(work.get_titles())
                if work.get_urn() is not None}

    @property
    def work_abbreviations(self):
        return {"%s$$n%i" % (work.get_urn(), i): abbrev
                for author in self.get_authors()
                for work in author.get_works()
                for i, abbrev in enumerate(work.get_abbreviations(combine=False) + work.get_abbreviations(combine=True))}

    def get_resource_by_urn(self, urn):
        """Fetch the resource corresponding to the input CTS URN.

        Currently supports
        only HucitAuthor and HucitWork.

        :param urn: the CTS URN of the resource to fetch
        :return: either an instance of `HucitAuthor` or of `HucitWork`

        """
        search_query = """
            PREFIX frbroo: <http://erlangen-crm.org/efrbroo/>
            PREFIX crm: <http://erlangen-crm.org/current/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?resource_URI

            WHERE {
                ?resource_URI crm:P1_is_identified_by ?urn .
                ?urn a crm:E42_Identifier .
                ?urn rdfs:label "%s"
            }
        """ % urn
        # check type of the input URN
        try:
            assert isinstance(urn, CTS_URN)
        except Exception as e:
            # convert to pyCTS.CTS_URN if it's a string
            urn = CTS_URN(urn)
            logger.debug('Converted the input urn from string to %s' % type(
                CTS_URN
            ))

        if (urn.work is not None):
            Work = self._session.get_class(surf.ns.EFRBROO['F1_Work'])
            result = self._store.execute_sparql(search_query)
            if len(result['results']['bindings']) == 0:
                raise ResourceNotFound
            else:
                tmp = result['results']['bindings'][0]
                resource_uri = tmp['resource_URI']['value']
                return self._session.get_resource(resource_uri, Work)

        elif (urn.work is None and urn.textgroup is not None):
            Person = self._session.get_class(surf.ns.EFRBROO['F10_Person'])
            result = self._store.execute_sparql(search_query)
            if len(result['results']['bindings']) == 0:
                raise ResourceNotFound
            else:
                tmp = result['results']['bindings'][0]
                resource_uri = tmp['resource_URI']['value']
                return self._session.get_resource(resource_uri, Person)

    # TODO: if the underlying store is not Virtuoso it should fail
    # and say something useful ;-)
    def search(self, search_string):
        """
        Searches for a given string through the resources' labels.

        :param search_string:
        :return: an instance of `HucitAuthor` or `HucitWork`.
        """
        query = """
        SELECT ?s ?label ?type
        WHERE {
            ?s a ?type .
            ?s rdfs:label ?label .
            ?label bif:contains "'%s'" .
        }
        """ % search_string
        response = self._session.default_store.execute_sparql(query)
        results = [(result['s']['value'], result['label']['value'], result['type']['value'])
                                                            for result in response["results"]["bindings"]]
        resources = [(label, self._session.get_resource(subject, self._session.get_class(type)))
                                                            for subject, label, type in results]

        Name = self._session.get_class(surf.ns.EFRBROO['F12_Name'])
        Title = self._session.get_class(surf.ns.EFRBROO['E35_Title'])
        Work = self._session.get_class(surf.ns.EFRBROO['F1_Work'])
        Person = self._session.get_class(surf.ns.EFRBROO['F10_Person'])

        result = []
        for label, resource in resources:
            if resource.uri == surf.ns.EFRBROO['E35_Title']:
                work = Work.get_by(efrbroo_P102_has_title = resource).first()
                result.append((label, work))
            elif resource.uri == surf.ns.EFRBROO['F12_Name']:
                author = Person.get_by(ecrm_P1_is_identified_by = resource).first()
                result.append((label, author))
            elif resource.uri == surf.ns.ECRM['E41_Appellation']:
                try:
                    name = Name.get_by(ecrm_P139_has_alternative_form = resource).first()
                    assert name is not None
                    author = Person.get_by(ecrm_P1_is_identified_by = name).first()
                    result.append((label, author))
                except Exception as e:
                    title = Title.get_by(ecrm_P139_has_alternative_form=resource).first()
                    assert title is not None
                    work = Work.get_by(efrbroo_P102_has_title = title).first()
                    result.append((label, work))
        return result

    def get_authors(self):
        """
        Returns the authors in the Knowledge Base.

        :return: a list of `HucitAuthor` instances.

        """
        Person = self._session.get_class(surf.ns.EFRBROO['F10_Person'])
        return list(Person.all())

    def get_works(self):
        """Return the author's works.

        :return: a list of `HucitWork` instances.

        """
        Work = self._session.get_class(surf.ns.EFRBROO['F1_Work'])
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
                la_names = sorted([name[1] for name in names if name[0] == "la"], key=len)
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

    def get_author_of(self):  # TODO finish
        pass

    def get_statistics(self):
        """
        Gather basic stats about the Knowledge Base and its contents.

        :return: a dictionary

        """
        statistics = {
            "number_authors": 0,
            "number_author_names": 0,
            "number_author_abbreviations": 0,
            "number_works": 0,
            "number_work_titles": 0,
            "number_title_abbreviations": 0,
            "number_opus_maximum":0,
        }
        for author in self.get_authors():
            if author.get_urn() is not None:
                opmax = True if self.get_opus_maximum_of(author.get_urn())\
                    is not None else False
                if opmax:
                    statistics["number_opus_maximum"] += 1
            statistics["number_authors"] += 1
            statistics["number_author_names"] += len(author.get_names())
            statistics["number_author_abbreviations"] += len(
                author.get_abbreviations()
            )
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

    def get_name_of(self): # TODO implement
        pass

    def get_title_of(self): # TODO implement
        pass

    def to_json(self):
        """
        Serialises the content of the KnowledgeBase as JSON.

        :return: TODO
        """
        return json.dumps({
            "statistics": self.get_statistics()
            , "authors": [json.loads(author.to_json()) for author in self.get_authors()]
        }, indent=2)
