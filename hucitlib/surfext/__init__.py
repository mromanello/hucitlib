#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com

"""
TODO: Description of the package.
"""

import os
import pdb
import json
import surf
import logging
import itertools
from collections import namedtuple
from typing import List, Dict, Optional, Union, NamedTuple
from surf import *
from surf.resource import Resource
from surf.exceptions import NoResultFound
from retrying import retry
from pyCTS import CTS_URN
from rdflib import Literal

logger = logging.getLogger("__name__")

surf.ns.register(ecrm="http://erlangen-crm.org/current/")
surf.ns.register(efrbroo="http://erlangen-crm.org/efrbroo/")
surf.ns.register(hucit="http://purl.org/net/hucit#")
surf.ns.register(kb="http://purl.org/hucit/kb/")

# TODO: define base URIs for entities (authors, works, types, names, URNs, etc.)
BASE_URI_TYPES = surf.ns.KB["types/%s"]
BASE_URI_AUTHORS = surf.ns.KB["authors/%s"]
BASE_URI_WORKS = surf.ns.KB["works/%s"]


class CitationLevel(NamedTuple):
    level: int
    label: str
    text_element_type: Resource
    count: int


class HucitAuthor(object):
    """
    Object mapping for class `frbroo:F10_Person <http://erlangen-crm.org/efrbroo/>`_.
    """

    def __repr__(self):
        names = ["%s (@%s)" % (name[1], name[0]) for name in self.get_names()]
        return f'HucitAuthor (names=[{",".join(names)}],urn={self.get_urn()})'

    def __str__(self):
        names = self.get_names()
        try:
            english_name = [name[1] for name in names if name[0] == "en"]
            return english_name[0]
        except Exception as e:
            try:
                default_name = [name[1] for name in names if name[0] == None]
                return default_name[0]
            except Exception as e:
                try:
                    latin_name = [name[1] for name in names if name[0] == "la"]
                    return latin_name[0]
                except Exception as e:
                    return None

    def get_names(self) -> Dict[str, str]:
        """Returns a list of author's name variants.

        :return: A dictionary where key is the language and value is the name in that language.
        :rtype: Dict[str]

        Example:

        .. code-block:: python

            >>> homer = kb.get_resource_by_urn('urn:cts:greekLit:tlg0012')
            >>> homer.get_names()
            [('en', 'Homer'),
            (None, 'Homeros'),
            ('la', 'Homerus'),
            ('fr', 'Homère'),
            ('it', 'Omero')]
        """
        names = [
            id
            for id in self.ecrm_P1_is_identified_by
            if id.uri == surf.ns.EFRBROO["F12_Name"]
        ]
        self.names = []
        for name in names:
            for variant in name.rdfs_label:
                self.names.append((variant.language, variant.title()))
        return self.names

    def add_name(self, name: str, lang: str = None) -> bool:
        """Adds a new name variant to an author’s name.

        :param str name: The name variant to be added.
        :param str lang: The language of the name variant.
        :return: `True` if the name is added, `False` otherwise (the name is a duplicate)
        :rtype: bool

        """
        try:
            assert (lang, name) not in self.get_names()
        except Exception as e:
            # TODO: raise a custom exception
            logger.warning(
                'Duplicate name detected while adding "%s (lang=%s)"' % (name, lang)
            )
            return False
        newlabel = Literal(name, lang=lang) if lang is not None else Literal(name)
        name = [
            id
            for id in self.ecrm_P1_is_identified_by
            if id.uri == surf.ns.EFRBROO["F12_Name"]
        ][0]
        try:
            name.rdfs_label.append(newlabel)
            name.update()  # this is currently buggy in SURF (see my NOTES.md)
            return True
        except Exception as e:
            raise e

    def remove_name(self, name_to_remove):  # TODO implement
        name = [
            id
            for id in self.ecrm_P1_is_identified_by
            if id.uri == surf.ns.EFRBROO["F12_Name"]
        ][0]

        for label in name.rdfs_label:
            if str(label) == name_to_remove:
                name.rdfs_label.pop(name.rdfs_label.index(label))
                name.update()
                return True
            else:
                pass
        return False

    def add_abbreviation(self, new_abbreviation) -> bool:
        """
        Adds a new name abbreviation to an author's name.

        :param new_abbreviation: the abbreviation to be added
        :return: `True` if the abbreviation is added, `False` otherwise (the abbreviation is a duplicate)
        """
        try:
            assert new_abbreviation not in self.get_abbreviations()
        except Exception as e:
            # TODO: raise a custom exception
            logger.warning(
                'Duplicate abbreviation detected while adding "%s"' % new_abbreviation
            )
            return False

        try:
            type_abbreviation = self.session.get_resource(
                BASE_URI_TYPES % "abbreviation",
                self.session.get_class(surf.ns.ECRM["E55_Type"]),
            )
            abbreviation = [
                abbreviation
                for name in self.ecrm_P1_is_identified_by
                for abbreviation in name.ecrm_P139_has_alternative_form
                if name.uri == surf.ns.EFRBROO["F12_Name"]
                and abbreviation.ecrm_P2_has_type.first == type_abbreviation
            ][0]
            abbreviation.rdfs_label.append(Literal(new_abbreviation))
            abbreviation.update()
            return True
        except IndexError as e:
            # means there is no abbreviation instance yet
            type_abbreviation = self.session.get_resource(
                BASE_URI_TYPES % "abbreviation",
                self.session.get_class(surf.ns.ECRM["E55_Type"]),
            )
            Appellation = self.session.get_class(surf.ns.ECRM["E41_Appellation"])
            abbreviation_uri = "%s/abbr" % str(self.subject)
            abbreviation = Appellation(abbreviation_uri)
            abbreviation.ecrm_P2_has_type = type_abbreviation
            abbreviation.rdfs_label.append(Literal(new_abbreviation))
            abbreviation.save()

            name = (
                name
                for name in self.ecrm_P1_is_identified_by
                if name.uri == surf.ns.EFRBROO["F12_Name"]
            ).next()
            name.ecrm_P139_has_alternative_form = abbreviation
            name.update()
            return True
        except Exception as e:
            raise e

    def get_abbreviations(self) -> List[str]:
        """Get abbreviations of the names of the author.

        :return: A list of known abbreviations.
        :rtype: List[str]

        Example:

        .. code-block:: python

            >>> kb = KnowledgeBase()
            >>> homer = kb.get_resource_by_urn('urn:cts:greekLit:tlg0012')
            >>> homer.get_abbreviations()
            ['Hom.']
        """
        abbreviations = []
        try:
            type_abbreviation = self.session.get_resource(
                BASE_URI_TYPES % "abbreviation",
                self.session.get_class(surf.ns.ECRM["E55_Type"]),
            )
            abbreviations = [
                str(label)
                for name in self.ecrm_P1_is_identified_by
                for abbreviation in name.ecrm_P139_has_alternative_form
                for label in abbreviation.rdfs_label
                if name.uri == surf.ns.EFRBROO["F12_Name"]
                and abbreviation.ecrm_P2_has_type.first == type_abbreviation
            ]
        except Exception as e:
            logger.debug("Exception raised when getting abbreviations for %a" % self)
        finally:
            return abbreviations

    def get_urn(self) -> Optional[CTS_URN]:
        """Returns the author's CTS URN.

        .. note::

            It is assumed that each HucitAuthor has only one CTS URN.

        :return: Description of returned object.
        :rtype: Optional[CTS_URN]

        """
        # TODO: check type
        try:
            type_ctsurn = self.session.get_resource(
                BASE_URI_TYPES % "CTS_URN",
                self.session.get_class(surf.ns.ECRM["E55_Type"]),
            )
            urn = [
                CTS_URN(identifier.rdfs_label.one)
                for identifier in self.ecrm_P1_is_identified_by
                if identifier.uri == surf.ns.ECRM["E42_Identifier"]
                and identifier.ecrm_P2_has_type.first.subject == type_ctsurn.subject
            ][0]
            return urn
        except Exception as e:
            return None

    def set_urn(self, urn: str) -> Optional[CTS_URN]:
        """Changes the CTS URN of the author or adds a new one (if no URN is assigned).

        :param str urn: The new CTS URN.
        :return: Description of returned object.
        :rtype: Optional[CTS_URN]

        """
        Type = self.session.get_class(surf.ns.ECRM["E55_Type"])
        Identifier = self.session.get_class(surf.ns.ECRM["E42_Identifier"])
        id_uri = f"{self.subject}/cts_urn"
        id = Identifier(id_uri)
        if id.is_present():
            id.rdfs_label = Literal(urn)
            id.update()
        else:
            id.save()
            id.rdfs_label = Literal(urn)
            id.ecrm_P2_has_type = Type(BASE_URI_TYPES % "CTS_URN")
            id.update()
        self.load()
        return self.get_urn()

    def get_works(self) -> List["HucitWork"]:
        """
        Returns a list of the works (intances of `surf.Resource` and `HucitWork`)
        attributed to a given author.
        """
        works = []
        for creation in self.efrbroo_P14i_performed:
            try:
                for work in creation.efrbroo_R16_initiated:
                    works.append(work)
            except Exception:
                pass
        return works

    def to_json(self) -> None:
        """Serialises a HucitAuthor to a JSON formatted string.

        .. note::

            This method will probably be deprecated in the near future.

        Example:

        .. code-block:: python

            >> homer = kb.get_resource_by_urn("urn:cts:greekLit:tlg0012")
            >> homer.to_json()
            {
              "name_abbreviations": [
                "Hom."
              ],
              "urn": "urn:cts:greekLit:tlg0012",
              "works": [
                {
                  "urn": "urn:cts:greekLit:tlg0012.tlg001",
                  "titles": [
                    {
                      "language": "it",
                      "label": "Iliade"
                    },
                    {
                      "language": "la",
                      "label": "Ilias"
                    },
                    {
                      "language": "en",
                      "label": "Iliad"
                    },
                    {
                      "language": "de",
                      "label": "Ilias"
                    },
                    {
                      "language": "fr",
                      "label": "L'Iliade"
                    }
                  ],
                  "uri": "http://purl.org/hucit/kb/works/2815",
                  "title_abbreviations": [
                    "Il."
                  ]
                },
                ...
              ],
              "uri": "http://purl.org/hucit/kb/authors/927",
              "names": [
                {
                  "language": "fr",
                  "label": "Hom\u00e8re"
                },
                {
                  "language": "la",
                  "label": "Homerus"
                },
                {
                  "language": null,
                  "label": "Homeros"
                },
                {
                  "language": "en",
                  "label": "Homer"
                },
                {
                  "language": "it",
                  "label": "Omero"
                }
              ]
            }
        """
        names = self.get_names()
        return json.dumps(
            {
                "uri": self.subject,
                "urn": str(self.get_urn()),
                "names": [{"language": lang, "label": label} for lang, label in names],
                "name_abbreviations": self.get_abbreviations(),
                "works": [json.loads(work.to_json()) for work in self.get_works()],
            },
            indent=2,
        )


class HucitTextStructure(object):
    """
    Object mapping for instances of `http://purl.og/net/hucit#TextStructure`.
    """

    def add_element(self, text_element, top_level=False) -> None:
        # TODO: the problem here is that the change to text element
        # is not saved
        text_element.context = self.subject
        if top_level:
            self.hucit_has_element.append(text_element)
            self.update()
        else:
            logger.debug(
                f"{text_element} not added to {self.subject} as it is not a top-level element"
            )
            pass

    @property
    def work(self):
        """Returns the parent object (`HucitWork`)."""
        Work = self.session.get_class(surf.ns.EFRBROO["F1_Work"])
        return Work.get_by(hucit_has_structure=self).first()


class HucitWork(object):
    """
    Object mapping for instances of `http://erlangen-crm.org/efrbroo/F1_Work`.
    """

    def __repr__(self):
        """Returns a string representation of a `HucitWork`."""
        titles = ["%s (@%s)" % (title[1], title[0]) for title in self.get_titles()]
        return f'HucitWork (title=[{",".join(titles)}],urn={self.get_urn()})'

    def __str__(self):
        """
        TODO: finish
        """
        titles = self.get_titles()
        try:
            english_title = [title[1] for title in titles if title[0] == "en"]
            return english_title[0]
        except Exception as e:
            try:
                default_title = [title[1] for title in titles if title[0] == None]
                return default_title[0]
            except Exception as e:
                try:
                    latin_title = [title[1] for title in titles if title[0] == "la"]
                    return latin_title[0]
                except Exception as e:
                    return None

    def get_titles(self):
        """TODO"""
        return [
            (label.language, str(label))
            for label in self.efrbroo_P102_has_title.first.rdfs_label
        ]

    def add_title(self, title, lang=None):
        """
        Adds a new title variant to a work.

        :param title: the title to be added
        :param lang: the language of the title variant
        :return: `True` if the title is added, `False` otherwise (the title is
            a duplicate)
        """
        try:
            assert (lang, title) not in self.get_titles()
        except Exception as e:
            # TODO: raise a custom exception
            logger.warning(
                "Duplicate title detected while adding {} (lang={})".format(
                    title, lang
                )
            )
            return False
        newlabel = Literal(title, lang=lang) if lang is not None else \
            Literal(title)
        title = self.efrbroo_P102_has_title.first
        try:
            title.rdfs_label.append(newlabel)
            title.update()
            return True
        except Exception as e:
            raise e

    def get_abbreviations(self, combine=False):
        """
        TODO: if `combine==True`, concatenate with author abbreviation(s)

        Get abbreviations of the titles of the work.

        :return: a list of strings (empty list if no abbreviations available).
        """
        abbreviations = []
        try:
            type_abbreviation = self.session.get_resource(
                BASE_URI_TYPES % "abbreviation",
                self.session.get_class(surf.ns.ECRM["E55_Type"]),
            )
            abbreviations = [
                str(label)
                for title in self.efrbroo_P102_has_title
                for abbreviation in title.ecrm_P139_has_alternative_form
                for label in abbreviation.rdfs_label
                if title.uri == surf.ns.EFRBROO["E35_Title"]
                and abbreviation.ecrm_P2_has_type.first == type_abbreviation
            ]

            if (
                combine
                and len(abbreviations) > 0
                and len(self.author.get_abbreviations()) >= 1
            ):
                abbreviations = [
                    "%s %s" % (author_abbrev, work_abbrev)
                    for author_abbrev, work_abbrev in itertools.product(
                        self.author.get_abbreviations(), self.get_abbreviations()
                    )
                ]
        except Exception as e:
            logger.debug("Exception raised when getting abbreviations for %a" % self)
        finally:
            return abbreviations

    def add_abbreviation(self, new_abbreviation):
        """
        Adds a new name variant to a work.

        :param new_abbreviation: the abbreviation to be added
        :return: `True` if the abbreviation is added, `False` otherwise (the abbreviation is a duplicate)
        """
        try:
            assert new_abbreviation not in self.get_abbreviations()
        except Exception as e:
            # TODO: raise a custom exception
            logger.warning(
                'Duplicate abbreviation detected while adding "%s"' % new_abbreviation
            )
            return False
        try:
            type_abbreviation = self.session.get_resource(
                BASE_URI_TYPES % "abbreviation",
                self.session.get_class(surf.ns.ECRM["E55_Type"]),
            )
            abbreviation = [
                abbreviation
                for title in self.efrbroo_P102_has_title
                for abbreviation in title.ecrm_P139_has_alternative_form
                if title.uri == surf.ns.EFRBROO["E35_Title"]
                and abbreviation.ecrm_P2_has_type.first == type_abbreviation
            ][0]
            abbreviation.rdfs_label.append(Literal(new_abbreviation))
            abbreviation.update()
            return True
        except IndexError as e:
            # means there is no name instance yet
            type_abbreviation = self.session.get_resource(
                BASE_URI_TYPES % "abbreviation",
                self.session.get_class(surf.ns.ECRM["E55_Type"]),
            )
            Appellation = self.session.get_class(surf.ns.ECRM["E41_Appellation"])
            abbreviation_uri = "%s/abbr" % str(self.subject)
            abbreviation = Appellation(abbreviation_uri)
            abbreviation.ecrm_P2_has_type = type_abbreviation
            abbreviation.rdfs_label.append(Literal(new_abbreviation))
            abbreviation.save()
            title = self.efrbroo_P102_has_title.first
            title.ecrm_P139_has_alternative_form = abbreviation
            title.update()
            return True
        except Exception as e:
            raise e

    def get_urn(self):
        """
        Get the CTS URN that identifies the work.

        :return: an instance of `pyCTS.CTS_URN` or None
        """
        try:
            type_ctsurn = self.session.get_resource(
                BASE_URI_TYPES % "CTS_URN",
                self.session.get_class(surf.ns.ECRM["E55_Type"]),
            )
            urn = [
                CTS_URN(identifier.rdfs_label.one)
                for identifier in self.ecrm_P1_is_identified_by
                if identifier.uri == surf.ns.ECRM["E42_Identifier"]
                and identifier.ecrm_P2_has_type.first.subject == type_ctsurn.subject
            ][0]
            return urn
        except Exception as e:
            return None

    def set_urn(self, urn):
        """
        Change the CTS URN of the author or adds a new one (if no URN is assigned).
        """
        Type = self.session.get_class(surf.ns.ECRM["E55_Type"])
        Identifier = self.session.get_class(surf.ns.ECRM["E42_Identifier"])
        id_uri = "%s/cts_urn" % str(self.subject)
        try:
            id = Identifier(id_uri)
            id.rdfs_label = Literal(urn)
            id.ecrm_P2_has_type = Type(BASE_URI_TYPES % "CTS_URN")
            id.save()
            return True
        except Exception as e:
            raise e

    def has_text_structure(self):
        """
        Checks whether a citable text structure is defined.

        :return: boolean
        """
        return len(self.hucit_has_structure) > 0

    def add_text_structure(self, label: str, lang: str = "en"):
        """
        Adds a citable text structure to the work.
        """

        ts = self.session.get_resource(
            "%s/text_structure" % self.subject,
            self.session.get_class(surf.ns.HUCIT["TextStructure"]),
        )
        ts.rdfs_label.append(Literal(label, lang))
        ts.save()
        self.hucit_has_structure = ts
        self.update()
        return self.hucit_has_structure.one

    def remove_text_structure(self, text_structure) -> None:
        # TODO: delete also TextElements one by one
        """
        Remove any citable text structure to the work.
        """
        idx = self.hucit_has_structure.index(text_structure)
        ts = self.hucit_has_structure.pop(idx)
        ts.remove()
        self.update()
        return

    # TODO finish implementation
    def get_citation_structure(self) -> List[CitationLevel]:
        """
        Returns a sorted list of citation levels
            [
                (1, 'book', ...),
                (2, 'line', ...),
            ]
        """
        pass

    # TODO finish implementation
    def get_citable_elements(self, CitationLevel):
        pass

    @property
    def structure(self):
        return self.hucit_has_structure.first

    def _get_opus_maximum(self):
        """Instantiate an opus maximum type."""
        label = """The opux maximum of a given author
                    that is, the only preserved work by that
                    author or the most known one."""

        opmax = self.session.get_resource(
            BASE_URI_TYPES % "opmax", self.session.get_class(surf.ns.ECRM["E55_Type"])
        )
        if opmax.is_present():
            return opmax
        else:
            opmax.rdfs_label.append(Literal(label, "en"))
            logger.debug("Created a new opus maximum type instance")
            opmax.save()
            return opmax

    def set_as_opus_maximum(self):  # TODO: test
        """Mark explicitly the work as the author's opus maximum."""
        if self.is_opus_maximum():
            return False
        else:
            opmax = self._get_opus_maximum()
            self.ecrm_P2_has_type = opmax
            self.update()
            return True

    def is_opus_maximum(self):
        """Check whether the work is the author's opus maximum.

        Two cases:
        1. the work is flagged as opus max
        2. there is only one work by this author

        :return: boolean
        """
        opmax = self._get_opus_maximum()
        types = self.ecrm_P2_has_type

        if opmax in types:
            return True
        else:
            if len(self.author.get_works()) == 1:
                return True
            else:
                return False

    @property
    def author(self) -> HucitAuthor:
        """
        Returns the author to whom the work is attributed.

        :return: an instance of `HucitWork` # TODO: check that's the case
        """
        CreationEvent = self.session.get_class(surf.ns.EFRBROO["F27_Work_Conception"])
        Person = self.session.get_class(surf.ns.EFRBROO["F10_Person"])
        creation_event = CreationEvent.get_by(efrbroo_R16_initiated=self).first()
        return Person.get_by(efrbroo_P14i_performed=creation_event).first()

    @property
    def structure(self) -> HucitTextStructure:
        try:
            return self.hucit_has_structure.one
        except NoResultFound:
            return None

    def get_top_elements(self):
        """
        TODO
        """
        pass

    def to_json(self):
        """
        Serialises a HucitWork to a JSON formatted string.
        """
        titles = self.get_titles()
        return json.dumps(
            {
                "uri": self.subject,
                "urn": str(self.get_urn()),
                "titles": [
                    {"language": lang, "label": label} for lang, label in titles
                ],
                "title_abbreviations": self.get_abbreviations(),
            },
            indent=2,
        )


class HucitTextElement(object):
    """
    Object mapping for instances of `http://purl.og/net/hucit#TextElement`.
    """

    def __repr__(self):
        return f"{self.rdfs_label.one} ({self.get_urn()})"

    def __str__(self):
        return "boh"

    @retry(stop_max_attempt_number=5, wait_fixed=5000)
    def add_relations(
        self,
        parent: Resource = None,
        previous: Resource = None,
        next: Resource = None,
    ) -> None:
        """Short summary.

        :param Resource parent: Description of parameter `parent`.
        :param Resource previous: Description of parameter `previous`.
        :param Resource next: Description of parameter `next`.
        :return: Description of returned object.
        :rtype: None

        """
        if next:
            self.hucit_precedes = next

        if previous:
            self.hucit_follows = previous

        if parent:
            self.hucit_is_part_of = parent

            # in this case add also the parent relation
            parent.hucit_has_part.append(self)
            parent.update()

        self.update()
        return

    @property
    def next(self) -> Optional[Resource]:
        """Returns the following text element (if any)."""
        try:
            return self.hucit_precedes.one
        except NoResultFound:
            return None

    @property
    def previous(self):
        """Returns the preceding text element (if any)."""
        try:
            return self.hucit_follows.one
        except NoResultFound:
            return None

    @property
    def children(self) -> List[Resource]:
        """ Returns the children text element(s) (if any)."""
        return self.hucit_has_part

    @property
    def parent(self):
        """Returns the parent (if any)."""
        try:
            return self.hucit_is_part_of.one
        except NoResultFound:
            return None

    def get_type(self, as_string: bool = True) -> Union[str, Resource]:
        """Short summary.

        :param bool as_string: Description of parameter `as_string`.
        :return: Description of returned object.
        :rtype: Union[str, Resource]

        """
        if as_string:
            return str(self.ecrm_P2_has_type.one.rdfs_label.one)
        else:
            return self.ecrm_P2_has_type.one

    def is_first(self):
        if self.previous is None:
            return True
        else:
            return False

    def is_last(self):
        if self.next is None:
            return True
        else:
            return False

    def get_urn(self) -> CTS_URN:
        """ Returns the TextElement's CTS URN."""
        # current assumption: only one CTS URN per element
        urn_string = self.ecrm_P1_is_identified_by.one.rdfs_label.one
        try:
            return CTS_URN(urn_string)
        except Exception as e:
            raise e
