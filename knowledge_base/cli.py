#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com

"""

Command line interface for a HuCit knowledge base.

Examples of usage:

	python knowledge_base/cli.py search "Aeneid"
	python knowledge_base/cli.py search “urn:cts:greekLit:tlg0012"
	python knowledge_base/cli.py add —-what=[name|abbr|title|sameas] —-to=“urn:cts:greekLit:tlg0012” “Omero"

Use memcached to store a cached kb, with an expiration date of a week or so. 
Store the KB as well as an instance of `CitationMatcher`. Or maybe just use the DictIndexer in pysuffix.

"""

import logging
from surfext import *
logger = logging.getLogger('KnowledgeBase_CLI')

def fetch_or_cache_knowledge_base():
	"""
	Returns a HuCit Knowledge Base, either fresh or cached.

	:return: an instance of `knowledge_base.KnowledgeBase`.

	"""
	pass
def fetch_or_cache_citation_matcher(knowledge_base):
	pass
def main():
	"""
	Define the CLI inteface/commands.
	"""
	pass
if __name__ == '__main__':
    main()