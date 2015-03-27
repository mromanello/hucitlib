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

class HucitAuthor(object):
        """ TODO """
        def __repr__(self):
            names = ["%s (@%s)"%(name[1],name[0]) for name in self.get_names()]
            return "HucitAuthor (names=[%s],urn=%s)"%(",".join(names),self.get_urn())
        def get_names(self):
            """

            Returns a dict where key is the language and value is the name in that language.
            Problem: only one label with lang will be returned (same key `None` is used)
            
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
        def get_urn(self):
            """
            Assumes that each HucitAuthor has only one CTS URN.
            """
            # TODO: check type
            type_ctsurn = self.session.get_resource('http://phd.mr56k.info/data/types#CTS_URN',self.session.get_class(surf.ns.ECRM['E55_Type']))
            urn = [CTS_URN(urnstring.rdfs_label.one) for urnstring in self.ecrm_P1_is_identified_by if urnstring.uri == surf.ns.ECRM['E42_Identifier'] and urnstring.ecrm_P2_has_type.first == type_ctsurn][0]
            return urn
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
            
            pass
        def get_works(self):
            """
            TODO
            """
            return [work  for creation in self.efrbroo_P14i_performed for work in creation.efrbroo_R16_initiated]

class HucitWork(object):
    """docstring for HucitWork"""
    def __repr__(self):
        """TODO"""
        titles = ["%s (@%s)"%(title[1],title[0]) for title in self.get_titles()]
        return "HucitWork (title=[%s],urn=%s)"%(",".join(titles),self.get_urn())
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
    def __str__(self):
        return unicode(self)
    def get_titles(self):
        """TODO"""
        return [(label.language,label.title()) for label in self.efrbroo_P102_has_title.first.rdfs_label]
    def get_urn(self):
        """TODO"""
        type_ctsurn = self.session.get_resource('http://phd.mr56k.info/data/types#CTS_URN',self.session.get_class(surf.ns.ECRM['E55_Type']))
        urn = [CTS_URN(urnstring.rdfs_label.one) for urnstring in self.ecrm_P1_is_identified_by if urnstring.uri == surf.ns.ECRM['E42_Identifier'] and urnstring.ecrm_P2_has_type.first == type_ctsurn][0]
        return urn
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
        pass
    def get_citation_levels(self):
        """
        Returns the levels of the TextStructure of this Work, in the right order (e.g. Book/Chapter/Section).
        """
        pass
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
    
        

