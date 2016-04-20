#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com

import ConfigParser
import surf
import logging
from surfext import HucitAuthor
from surfext import HucitWork
from pyCTS import CTS_URN

logger = logging.getLogger('KnowledgeBase')

class KnowledgeBase(object):
	"""

	>>> #import sys
	>>> #sys.path.append('/Users/rromanello/Documents/knowledge_base/')
	>>> #import knowledge_base
	>>> #from knowledge_base import KnowledgeBase
	>>> kb = KnowledgeBase('/Users/rromanello/Documents/knowledge_base/agraph.ini')
	>>> temp = kb.get_author_label('urn:cts:cwkb:903')

	"""
	def _register_mappings(self):
		self._session.mapping[surf.ns.EFRBROO.F10_Person] = HucitAuthor
		self._session.mapping[surf.ns.EFRBROO.F1_Work] = HucitWork
		return
	def _register_namespaces(self):
		surf.ns.register(ecrm="http://erlangen-crm.org/current/")
		surf.ns.register(efrbroo="http://erlangen-crm.org/efrbroo/")
		surf.ns.register(hucit="http://purl.org/net/hucit#")
		return
	def __init__(self, config_file):
		"""
		TODO: support also the use of an in-memory store,
			with data loaded from the `data` directory
		"""
		try:
			config = ConfigParser.ConfigParser()
			config.readfp(open(config_file))
			self._store_params = dict(config.items("surf"))
			self._store_params['port'] = int(self._store_params['port']) # force the `port` to be an integer
			self._store=surf.Store(**self._store_params)
			self._session = surf.Session(self._store, {})
			self._register_namespaces()
			self._register_mappings()
		except Exception, e:
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
	def __setstate__(self,dict):
		self.__dict__.update(dict)
		self._store = surf.Store(**self._store_params)
		self._session = surf.Session(self._store, {})
		self._register_namespaces()
		self._register_mappings()
	def get_resource_by_urn(self,urn):
		"""
		
		Fetch from the KnowledgeBase the resource object
		corresponding to the input CTS URN. Currently supports
		only HucitAuthor and HucitWork. 

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
		"""%urn
		try: #check type of the input URN
			assert type(urn) == type(CTS_URN(str(urn)))
		except Exception, e: #convert to pyCTS.CTS_URN if it's a string
			logger.debug('Converted the input urn from string to %s'%type(CTS_URN))
			urn = CTS_URN(urn)
		if(urn.work is not None):
			Work = self._session.get_class(surf.ns.EFRBROO['F1_Work'])
			result = self._store.execute_sparql(search_query)
			resource_uri = result['results']['bindings'][0]['resource_URI']['value']
			return self._session.get_resource(resource_uri,Work)
		elif(urn.work is None and urn.textgroup is not None):
			Person = self._session.get_class(surf.ns.EFRBROO['F10_Person'])
			result = self._store.execute_sparql(search_query)
			resource_uri = result['results']['bindings'][0]['resource_URI']['value']
			return self._session.get_resource(resource_uri,Person)
	def get_authors(self):
		"""

		Returns the list of authors in the KB (type=`HucitAuthor`)
		
		"""
		Person = self._session.get_class(surf.ns.EFRBROO['F10_Person'])
		return list(Person.all())
	def get_works(self):
		"""
		
		Returns the list of works in the KB (type=`HucitWork`)
		
		"""
		Work = self._session.get_class(surf.ns.EFRBROO['F1_Work'])
		return list(Work.all())
	def get_author_label(self,urn):
		"""

		Get the label corresponding to the author identified
		by the input CTS URN. 

		try to get an lang=en label (if multiple labels in this lang exist pick the shortest)
		try to get a lang=la label (if multiple labels in this lang exist pick the shortest)
		try to get a lang=None label (if multiple labels in this lang exist pick the shortest)

		returns None if no name is found

		"""
		author = self.get_resource_by_urn(urn)
		names = author.get_names()
		en_names = sorted([name[1] for name in names if name[0]=="en"],key=len)
		try:
			assert len(en_names) > 0
			return en_names[0]
		except Exception, e:
			none_names = sorted([name[1] for name in names if name[0]==None],key=len)
			try:
				return none_names[0]
			except Exception, e:
				la_names = sorted([name[1] for name in names if name[0]=="la"],key=len)
				try:
					assert len(la_names) > 0
					return la_names[0]
				except Exception, e:
					return None
	def get_work_label(self,urn):
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
		en_titles = [title[1] for title in titles if title[0]=="en"]
		try:
			assert len(en_titles) > 0
			return en_titles[0]
		except Exception, e:
			la_titles = [title[1] for title in titles if title[0]==None]
			try:
				assert len(la_titles) > 0
				return la_titles[0]
			except Exception, e:
				none_titles = [title[1] for title in titles if title[0]=="la"]
				try:
					return none_titles[0]
				except Exception, e:
					return None
	def get_author_of(self): # TODO finish
		pass
	def to_json(self):
		"""
		Serialise the content of the KnowledgeBase as JSON
		"""
		pass

