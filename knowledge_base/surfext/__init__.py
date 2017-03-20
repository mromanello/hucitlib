#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com

"""
TODO: Description of the package.
"""

import pdb
import json
import surf
import logging
from surf import *
from pyCTS import CTS_URN
from rdflib import Literal

logger = logging.getLogger('')

surf.ns.register(ecrm="http://erlangen-crm.org/current/")
surf.ns.register(efrbroo="http://erlangen-crm.org/efrbroo/")
surf.ns.register(hucit="http://purl.org/net/hucit#")
surf.ns.register(kb="http://128.178.21.39:8080/matteo-data/")

# TODO: define base URIs for entities (authors, works, types, names, URNs, etc.)
BASE_URI_TYPES = surf.ns.KB["types#"]
BASE_URI_AUTHORS = surf.ns.KB["authors#"]
BASE_URI_WORKS = surf.ns.KB["works#"]

class HucitAuthor(object):
    """
    Object mapping for instances of `http://erlangen-crm.org/efrbroo/F10_Person`.
    """
    def __repr__(self):
        names = ["%s (@%s)"%(name[1],name[0]) for name in self.get_names()]
        return ("HucitAuthor (names=[%s],urn=%s)"%(",".join(names),self.get_urn())).encode("utf-8")
    def __unicode__(self):
        names = self.get_names()
        try:
            english_name = [name[1] for name in names if name[0]=='en']
            return english_name[0]
        except Exception, e:
            try:
                default_name = [name[1] for name in names if name[0]==None]
                return default_name[0]
            except Exception, e:
                try:
                    latin_name = [name[1] for name in names if name[0]=='la']
                    return latin_name[0]
                except Exception, e:
                    return None
    def get_names(self):
        """
        Returns a dict where key is the language and value is the name in that language.
        
        Example:
            {'it':"Sofocle"}
        """
        names = [id for id in self.ecrm_P1_is_identified_by if id.uri == surf.ns.EFRBROO['F12_Name']]
        self.names = []
        for name in names:
            for variant in name.rdfs_label:
                self.names.append((variant.language,variant.title()))
        return self.names
    def add_name(self, name, lang=None):
        """
        Adds a new name variant to an author.

        :param name: the name to be added 
        :param lang: the language of the name variant
        :return: `True` if the name is added, `False` otherwise (the name is a duplicate)
        """
        try:
            assert (lang, name) not in self.get_names()
        except Exception as e: 
            # TODO: raise a custom exception
            logger.warning("Duplicate name detected while adding \"%s (lang=%s)\""%(name, lang))
            return False
        newlabel = None
        if lang is not None:
            newlabel = Literal(name, lang=lang)
        else:
            newlabel = Literal(name)
        name = [id for id in self.ecrm_P1_is_identified_by if id.uri == surf.ns.EFRBROO['F12_Name']][0]
        try:
            name.rdfs_label.append(newlabel)
            name.save()
            return True
        except Exception as e:
            raise e
    def add_name_abbreviation(self, new_abbreviation):
        """
        Adds a new name variant to an author.

        :param new_abbreviation: the abbreviation to be added 
        :return: `True` if the abbreviation is added, `False` otherwise (the abbreviation is a duplicate)
        """
        try:
            assert new_abbreviation not in self.get_abbreviations()
        except Exception as e: 
            # TODO: raise a custom exception
            logger.warning("Duplicate abbreviation detected while adding \"%s\""%new_abbreviation)
            return False
        try:
            type_abbreviation = self.session.get_resource(surf.ns.KB["types#abbreviation"]
                                                        , self.session.get_class(surf.ns.ECRM['E55_Type']))
            abbreviation = [abbreviation 
                                for name in self.ecrm_P1_is_identified_by 
                                    for abbreviation in name.ecrm_P139_has_alternative_form
                                        if name.uri == surf.ns.EFRBROO['F12_Name'] 
                                            and abbreviation.ecrm_P2_has_type.first == type_abbreviation][0]
            abbreviation.rdfs_label.append(Literal(new_abbreviation))
            abbreviation.save()
            return True
        except Exception as e:
            raise e
    def get_abbreviations(self):
        """
        Get abbreviations of the names of the author.

        :return: a list of strings (empty list if no abbreviations available).
        """
        abbreviations = []
        try:
            type_abbreviation = self.session.get_resource(surf.ns.KB["types#abbreviation"]
                                                        , self.session.get_class(surf.ns.ECRM['E55_Type']))
            abbreviations = [label.title() 
                                for name in self.ecrm_P1_is_identified_by 
                                    for abbreviation in name.ecrm_P139_has_alternative_form
                                        for label in abbreviation.rdfs_label 
                                            if name.uri == surf.ns.EFRBROO['F12_Name'] 
                                                and abbreviation.ecrm_P2_has_type.first == type_abbreviation]
        except Exception as e:
            logger.debug("Exception raised when getting abbreviations for %a"%self)
        finally:
            return abbreviations
    def get_urn(self):
        """
        Assumes that each HucitAuthor has only one CTS URN.
        """
        # TODO: check type
        try:
            type_ctsurn = self.session.get_resource(surf.ns.KB["types#CTS_URN"]
                                                    , self.session.get_class(surf.ns.ECRM['E55_Type']))
            urn = [CTS_URN(urnstring.rdfs_label.one) 
                                for urnstring in self.ecrm_P1_is_identified_by 
                                                            if urnstring.uri == surf.ns.ECRM['E42_Identifier'] 
                                                            and urnstring.ecrm_P2_has_type.first == type_ctsurn][0]
            return urn
        except Exception as e:
            return None
    def set_urn(self,urn):
        """
        Change the CTS URN of the author or adds a new one (if no URN is assigned).
        """
        Type = self.session.get_class(surf.ns.ECRM['E55_Type'])
        Identifier = self.session.get_class(surf.ns.ECRM['E42_Identifier'])
        id_uri = "%s#cts_urn"%str(self.subject)
        try:
            id = Identifier(id_uri)
            id.rdfs_label = Literal(urn)
            id.ecrm_P2_has_type = Type(surf.ns.KB["types#CTS_URN"])
            id.save()
            return True
        except Exception, e:
            raise e 
    def get_works(self):
        """
        Returns a list of the works (intances of `surf.Resource` and `HucitWork`)
        attributed to a given author.
        """
        return [work  for creation in self.efrbroo_P14i_performed 
                                for work in creation.efrbroo_R16_initiated]
    def to_json(self):
        """
        Serialises a HucitAuthor to a JSON formatted string.

        Example:

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
              "uri": "http://128.178.21.39:8080/matteo-data/works/2815", 
              "title_abbreviations": [
                "Il."
              ]
            }, 
            {
              "urn": "urn:cts:greekLit:tlg0012.tlg002", 
              "titles": [
                {
                  "language": "en", 
                  "label": "Odyssey"
                }, 
                {
                  "language": "fr", 
                  "label": "L'Odyss\u00e9e"
                }, 
                {
                  "language": "it", 
                  "label": "Odissea"
                }, 
                {
                  "language": "la", 
                  "label": "Odyssea"
                }, 
                {
                  "language": "de", 
                  "label": "Odyssee"
                }
              ], 
              "uri": "http://128.178.21.39:8080/matteo-data/works/2816", 
              "title_abbreviations": [
                "Od."
              ]
            }, 
            {
              "urn": "urn:cts:cwkb:927.2814", 
              "titles": [
                {
                  "language": "la", 
                  "label": "Epigrammata"
                }
              ], 
              "uri": "http://128.178.21.39:8080/matteo-data/works/2814", 
              "title_abbreviations": [
                "Epigr."
              ]
            }
          ], 
          "uri": "http://128.178.21.39:8080/matteo-data/authors/927", 
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
        return json.dumps({    
                    "uri" : self.subject
                    , "urn" : str(self.get_urn())
                    , "names" : [{"language":lang, "label":label} for lang, label in names]
                    , "name_abbreviations" : self.get_abbreviations()
                    , "works" : [json.loads(work.to_json()) for work in self.get_works()]
                }, indent=2)
class HucitWork(object):
    """
    Object mapping for instances of `http://erlangen-crm.org/efrbroo/F1_Work`.
    """
    def __repr__(self):
        """TODO"""
        titles = ["%s (@%s)"%(title[1],title[0]) for title in self.get_titles()]
        return ("HucitWork (title=[%s],urn=%s)"%(",".join(titles),self.get_urn())).encode('utf-8')
    def __unicode__(self):
        """
        TODO: finish
        """
        titles = self.get_titles()
        try:
            english_title = [title[1] for title in titles if title[0]=='en']
            return english_title[0]
        except Exception, e:
            try:
                default_title = [title[1] for title in titles if title[0]==None]
                return default_title[0]
            except Exception, e:
                try:
                    latin_title = [title[1] for title in titles if title[0]=='la']
                    return latin_title[0]
                except Exception, e:
                    return None
    def get_titles(self):
        """TODO"""
        return [(label.language,label.title()) for label in self.efrbroo_P102_has_title.first.rdfs_label]
    def get_abbreviations(self, combine=False):
        """
        TODO: if `combine==True`, concatenate with author abbreviation(s)

        Get abbreviations of the titles of the work.

        :return: a list of strings (empty list if no abbreviations available).
        """
        abbreviations = []
        try:
            type_abbreviation = self.session.get_resource(surf.ns.KB["types#abbreviation"]
                                                        , self.session.get_class(surf.ns.ECRM['E55_Type']))
            abbreviations = [abbreviation.rdfs_label.one.title() 
                                for title in self.efrbroo_P102_has_title 
                                    for abbreviation in title.ecrm_P139_has_alternative_form
                                        if title.uri == surf.ns.EFRBROO['E35_Title'] 
                                            and abbreviation.ecrm_P2_has_type.first == type_abbreviation]
        except Exception as e:
            logger.debug("Exception raised when getting abbreviations for %a"%self)
        finally:
            return abbreviations
    def get_urn(self):
        """
        Get the CTS URN that identifies the work.

        :return: an instance of `pyCTS.CTS_URN` or None
        """
        try:
            type_ctsurn = self.session.get_resource(surf.ns.KB["types#CTS_URN"]
                                                    , self.session.get_class(surf.ns.ECRM['E55_Type']))
            urn = [CTS_URN(urnstring.rdfs_label.one) 
                            for urnstring in self.ecrm_P1_is_identified_by 
                                    if urnstring.uri == surf.ns.ECRM['E42_Identifier'] and 
                                        urnstring.ecrm_P2_has_type.first == type_ctsurn][0]
            return urn
        except Exception, e:
            return None
    def set_urn(self,urn):
        """
        Change the CTS URN of the author or adds a new one (if no URN is assigned).
        """
        Type = self.session.get_class(surf.ns.ECRM['E55_Type'])
        Identifier = self.session.get_class(surf.ns.ECRM['E42_Identifier'])
        id_uri = "%s#cts_urn"%str(self.subject)
        try:
            id = Identifier(id_uri)
            id.rdfs_label = Literal(urn)
            id.ecrm_P2_has_type = Type(surf.ns.KB["types#CTS_URN"])
            id.save()
            return True
        except Exception, e:
            raise e
    def has_text_structure(self):
        """
        Checks whether a citable text structure is defined.

        :return: boolean
        """
        pass
    def set_as_opus_maximum(self): # TODO: implement
        """
        Mark explicitly a work as the opus maximum.
        """
        pass
    def is_opus_maximum(self): # TODO: implement
        """
        Two cases:
        1. the work is flagged as opus max 
        2. there is only one work by this author

        :return: boolean
        """
        pass
    def get_citation_levels(self):
        """
        Returns the levels of the TextStructure of this Work, in the right order (e.g. Book/Chapter/Section).
        """
        pass
    @property
    def author(self):
        """
        Returns the author to whom the work is attributed.

        :return: an instance of `HucitWork` # TODO: check that's the case
        """
        CreationEvent = self.session.get_class(surf.ns.EFRBROO['F27_Work_Conception'])
        Person = self.session.get_class(surf.ns.EFRBROO['F10_Person'])
        creation_event =  CreationEvent.get_by(efrbroo_R16_initiated=self).first()
        return Person.get_by(efrbroo_P14i_performed = creation_event).first()
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
        return json.dumps({
                "uri" : self.subject
                , "urn" : str(self.get_urn())
                , "titles" : [{"language":lang, "label":label} for lang, label in titles]
                , "title_abbreviations" : self.get_abbreviations()

            }, indent=2)
class HucitTextElement(object):
    """
    Object mapping for instances of `http://purl.og/net/hucit#TextElement`.
    """
    def __repr__(self):
        return ""
    def next(self):
        """ TODO """
        return self.hucit_precedes.one
    def previous(self):
        """ TODO """
        return self.hucit_follows.one
    def get_labels(self):
        pass
    def children(self):
        """
        TODO: the children elements should be returned 
        as an ordered collection
        """
        pass
    def parent(self):
        pass
    def get_type(self):
        pass
    def is_first(self):
        pass
    def is_last(self):
        pass
    def get_urn(self):
        """
        TODO
        """
        urn = self.ecrm_P1_is_identified_by.one
        try:
            return CTS_URN(urn)
        except Exception, e:
            raise e
class HucitTextStructure(object):
    """
    Object mapping for instances of `http://purl.og/net/hucit#TextStructure`.
    """
    pass
class HucitCtsUrn(object):
    """
    TODO
    """
    def __init__(self, urn_string):
        """
        assign to it the right type
        """
        pass
        

