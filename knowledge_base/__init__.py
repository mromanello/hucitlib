#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com

import ConfigParser
import surf
import logging
from surfext import *
from pyCTS import CTS_URN
import pkg_resources

logger = logging.getLogger('KnowledgeBase')

# TODO: add exceptions => AuthorNotFound, WorkNotFound or perhaps just ResourceNotFound

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
			config = ConfigParser.ConfigParser()
			config.readfp(open(config_file))
			self._store_params = dict(config.items("surf"))
			if(self._store_params.has_key('port')):
				self._store_params['port'] = int(self._store_params['port']) # force the `port` to be an integer
			self._store=surf.Store(**self._store_params)
			self._session = surf.Session(self._store, {})
			if(self._store_params.has_key("rdflib_store")):
				basedir = pkg_resources.resource_filename('knowledge_base','data/kb/')
				sources = ["%s%s"%(basedir, file) for file in self._store_params["knowledge_base_sources"].split(",")]
				source_format = self._store_params["sources_format"]
				for source_path in sources:
					self._store.writer._graph.parse(source=source_path,format=source_format)
					#self._store.load_triples(source=source_path,format=source_format)
					logger.info("The KnowledgeBase contains %i triples"%self._store.size())
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
	def __setstate__(self,dict):
		self.__dict__.update(dict)
		self._store = surf.Store(**self._store_params)
		self._session = surf.Session(self._store, {})
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
		return {"%s$$n%i"%(author.get_urn(), i) : name[1] 
				for author in self.get_authors()
						for i, name in enumerate(author.get_names())
												if author.get_urn() is not None}
	@property
	def author_abbreviations(self):
		return {"%s$$n%i"%(author.get_urn(), i) : abbrev 
				for author in self.get_authors()
						for i, abbrev in enumerate(author.get_abbreviations())
												if author.get_urn() is not None}
	@property
	def work_titles(self):
		return {"%s$$n%i"%(work.get_urn(), i) : title[1] 
				for author in self.get_authors()
					for work in author.get_works()
						for i, title in enumerate(work.get_titles())
												if work.get_urn() is not None}
	@property
	def work_abbreviations(self):
		return {"%s$$n%i"%(work.get_urn(), i) : abbrev 
				for author in self.get_authors()
					for work in author.get_works()
						for i, abbrev in enumerate(work.get_abbreviations())}
	def get_resource_by_urn(self,urn):
		"""
		
		Fetch from the KnowledgeBase the resource object
		corresponding to the input CTS URN. Currently supports
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
		"""%urn
		try: #check type of the input URN
			assert type(urn) == type(CTS_URN(str(urn)))
		except Exception as e: #convert to pyCTS.CTS_URN if it's a string
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
		Returns the authors in the Knowledge Base.

		:return: a list of `HucitAuthor` instances.
		
		"""
		Person = self._session.get_class(surf.ns.EFRBROO['F10_Person'])
		return list(Person.all())
	def get_works(self):
		"""
		Returns the works in the Knowledge Base.

		:return: a list of `HucitWork` instances.
		
		"""
		Work = self._session.get_class(surf.ns.EFRBROO['F1_Work'])
		return list(Work.all())
	def get_author_label(self, urn):
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
		except Exception as e:
			none_names = sorted([name[1] for name in names if name[0]==None],key=len)
			try:
				return none_names[0]
			except Exception as e:
				la_names = sorted([name[1] for name in names if name[0]=="la"],key=len)
				try:
					assert len(la_names) > 0
					return la_names[0]
				except Exception as e:
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
		except Exception as e:
			la_titles = [title[1] for title in titles if title[0]==None]
			try:
				assert len(la_titles) > 0
				return la_titles[0]
			except Exception as e:
				none_titles = [title[1] for title in titles if title[0]=="la"]
				try:
					return none_titles[0]
				except Exception as e:
					return None
	def get_author_of(self): # TODO finish
		pass
	def get_statistics(self):
		"""
		Gather basic stats about the Knowledge Base and its contents.

		:return: a dictionary

		"""
		statistics = {
			"number_authors" : 0
			, "number_author_names" : 0
			, "number_author_abbreviations" : 0
			, "number_works" : 0
			, "number_work_titles" : 0
			, "number_title_abbreviations" : 0
		}
		for author in self.get_authors():
			statistics["number_authors"] += 1
			statistics["number_author_names"] += len(author.get_names())
			statistics["number_author_abbreviations"] += len(author.get_abbreviations())
			for work in author.get_works():
				statistics["number_works"] += 1
				statistics["number_work_titles"] += len(work.get_titles())
				statistics["number_title_abbreviations"] += len(work.get_abbreviations())
		return statistics
	def get_opus_maximum_of(self, author_cts_urn): # TODO implement
		"""
		given the CTS URN of an author, this method returns its opus maximum. 
		If not available returns None.

		:param author_cts_urn: the CTS URN of the author whose opus max is to be retrieved.
		:return: an instance of `surfext.HucitWork` or None

		""" 
		pass
	def to_json(self):
		"""
		Serialises the content of the KnowledgeBase as JSON.

		:return: TODO
		"""
		return {
			"statistics" : self.get_statistics()
			, "authors" : [author.to_json() for author in self.get_authors()] 
		} 
