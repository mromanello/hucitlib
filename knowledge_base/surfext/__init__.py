#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com

import surf
from surf import *
from pyCTS import CTS_URN
from rdflib import Literal

surf.ns.register(ecrm="http://erlangen-crm.org/current/")
surf.ns.register(efrbroo="http://erlangen-crm.org/efrbroo/")
surf.ns.register(hucit="http://purl.org/net/hucit#")
surf.ns.register(kb="http://128.178.21.39:8080/matteo-data/")

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
        def add_name(self,name,lang):
            """
            TODO
            """
            newlabel = None
            if lang is not None:
                newlabel = Literal(name, lang=lang)
            else:
                newlabel = Literal(name)
            name = [id for id in self.ecrm_P1_is_identified_by if id.uri == surf.ns.EFRBROO['F12_Name']][0]
            try:
                name.rdfs_label.append(newlabel)
                return True
            except Exception, e:
                print e
                return False
        def add_name_abbreviation(self):
            """TODO"""
            pass
        def get_abbreviations(self):
            """
            Get abbreviations of the names of the author.

            :return: a list of strings (empty list if no abbreviations available).
            """
            abbreviations = []
            try:
                type_abbreviation = self.session.get_resource(surf.ns.KB["types#abbreviation"]
                                                            , self.session.get_class(surf.ns.ECRM['E55_Type']))
                abbreviations = [abbreviation.rdfs_label.one 
                                    for name in self.ecrm_P1_is_identified_by 
                                        for abbreviation in name.ecrm_P139_has_alternative_form
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
                type_ctsurn = self.session.get_resource(surf.ns.KB["types#CTS_URN"],self.session.get_class(surf.ns.ECRM['E55_Type']))
                urn = [CTS_URN(urnstring.rdfs_label.one) for urnstring in self.ecrm_P1_is_identified_by if urnstring.uri == surf.ns.ECRM['E42_Identifier'] and urnstring.ecrm_P2_has_type.first == type_ctsurn][0]
                return urn
            except Exception as e:
                return None
        def set_urn(self,urn):
            """TODO: finish and test"""
            try:
                Identifier = self.session.get_class(surf.ns.ECRM['E42_Identifier'])
                Type = self.session.get_class(surf.ns.ECRM['E55_Type'])
                id_uri = "%s#cts_urn"%str(self.subject)
                id = Identifier(id_uri)
                id.rdfs_label = Literal(urn)
                type_ctsurn = self.session.get_resource(surf.ns.KB["types#CTS_URN"],Type)
                id.ecrm_P2_has_type = type_ctsurn
                return True
            except Exception, e:
                print e
                return False  
            pass
        def get_works(self):
            """
            Returns a list of the works (intances of `surf.Resource` and `HucitWork`)
            attributed to a given author.
            """
            return [work  for creation in self.efrbroo_P14i_performed 
                                    for work in creation.efrbroo_R16_initiated]
        def to_json(self):
            """
            TODO: returns a JSON representation of the object

            {
                uri : ""
                , urn : "urn:cts:xxx"
                , names : ["a", "b"]
                , name_abbreviations: ["a.", "b."]
                , works : [{}, {}]
            }
            """
            return {}
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
    def get_abbreviations(self):
        """
        Get abbreviations of the titles of the work.

        :return: a list of strings (empty list if no abbreviations available).
        """
        abbreviations = []
        try:
            type_abbreviation = self.session.get_resource(surf.ns.KB["types#abbreviation"]
                                                        , self.session.get_class(surf.ns.ECRM['E55_Type']))
            abbreviations = [abbreviation.rdfs_label.one 
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
            type_ctsurn = self.session.get_resource(surf.ns.KB["types#CTS_URN"],self.session.get_class(surf.ns.ECRM['E55_Type']))
            urn = [CTS_URN(urnstring.rdfs_label.one) for urnstring in self.ecrm_P1_is_identified_by if urnstring.uri == surf.ns.ECRM['E42_Identifier'] and urnstring.ecrm_P2_has_type.first == type_ctsurn][0]
            return urn
        except Exception, e:
            return None
    def set_urn(self,urn):
        """TODO: finish and test"""
        try:
            Identifier = self.session.get_class(surf.ns.ECRM['E42_Identifier'])
            Type = self.session.get_class(surf.ns.ECRM['E55_Type'])
            id_uri = "%s#cts_urn"%str(self.subject)
            id = Identifier(id_uri)
            id.rdfs_label = Literal(urn)
            type_ctsurn = self.session.get_resource('http://phd.mr56k.info/data/types#CTS_URN',Type)
            id.ecrm_P2_has_type = type_ctsurn
            return True
        except Exception, e:
            print e
            return False
    def has_text_structure(self):
        """
        Checks whether a citable text structure is defined.

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
class HucitTextElement(object):
    """docstring for HucitTextElement"""
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
    
        

