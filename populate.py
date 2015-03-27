#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com

import requests # http://docs.python-requests.org
from lxml import etree
import pprint
from pyCTS import CTS_URN # https://github.com/mromanello/CTS_dev
from surfext import *
from rdflib import Literal
import ConfigParser

# register the namespaces
surf.ns.register(ecrm="http://erlangen-crm.org/current/")
surf.ns.register(efrbroo="http://erlangen-crm.org/efrbroo/")
surf.ns.register(kb="http://data.mr56k.info/")

def create_text_element_type(class_name, label):
    """
    Creates an instance of E55_Type corresponding to a type of TextElement (e.g. book, line, etc.)
    """
    try:
        instance = class_name.get_by(rdfs_label=label).one()
        print "found an instance of %s in the 3store"%label
    except Exception, e:
        instance = class_name(surf.ns.KB["types/%s"%label])
        instance.rdfs_label = Literal(label)
        instance.save()
    finally:
        return instance
def create_text_element(class_name,urn,label,text_element_type,text_structure):
    """
    Creates an instance of HuCit:TextElement
    """
    try:
        instance = class_name(surf.ns.KB["works/%s"]%urn)
        instance.rdfs_label = Literal(label,lang="en")
        ctsurn_uri = "%s#cts_urn"%str(instance.subject)
        ctsurn = Identifier(ctsurn_uri)
        ctsurn.rdfs_label = Literal(label)
        ctsurn.save()
        instance.ecrm_P1_is_identified_by = ctsurn
        instance.ecrm_P2_has_type = text_element_type
        instance.save()
        text_structure.hucit_has_element.append(instance)
        text_structure.save()
        print >> sys.stderr, "created resource %s for %s"%(str(instance),urn)
        return instance
    except Exception, e:
        raise e
def create_part_of_relation(relation):
    """
    TODO
    """
    node1 = None,
    node2 = None,
    uri1 = surf.ns.KB["works/%s"%(relation[0])]
    uri2 = surf.ns.KB["works/%s"%(relation[1])]
    node1 = ss.get_resource(uri1,TextElement)
    node2 = ss.get_resource(uri2,TextElement)
    if(node1.is_present() and node2.is_present()):
        node1.hucit_is_part_of = node2
        node2.hucit_has_part = node1
        node1.update()
        node2.update()
def create_follows_relation(relation):
    """
    TODO
    """
    node1 = None,
    node2 = None,
    uri1 = surf.ns.KB["works/%s"%(relation[0])]
    uri2 = surf.ns.KB["works/%s"%(relation[1])]
    node1 = ss.get_resource(uri1,TextElement)
    node2 = ss.get_resource(uri2,TextElement)
    if(node1.is_present() and node2.is_present()):
        node1.hucit_follows = node2
        node2.hucit_precedes = node1
        node1.update()
        node2.update()
    return
def parse_perseus_catalog(perseus_getcap = "http://www.perseus.tufts.edu/hopper/CTS?request=GetCapabilities"):
    """
    >>> catalog = parse_perseus_catalog()
    # example of a textgroup record
    >>> print catalog[ 'urn:cts:latinLit:phi0134']
    {'groupname': 'P. Terentius Afer (Terence)', 'type': 'textgroup'}
    # example of a work record
    >>> print catalog[ 'urn:cts:latinLit:phi0134.phi003']
    {'versions': ['urn:cts:latinLit:phi0134.phi003.perseus-lat1', 'urn:cts:latinLit:phi0134.phi003.perseus-eng1']
    , 'type': 'work', 'title': 'The Eunuch'}
    # example of an edition record
    >>> print catalog['urn:cts:latinLit:phi0134.phi003.perseus-lat1']
    {'type': 'edition', 'citation_levels': ['act', 'scene', 'line']}

    """
    def get_citation_levels(element):
        """
        recursive function to extract a list of citation levels.
        takes a CitationMapping element as input.
        """
        temp = element.xpath('.//d:citation ',namespaces=ns)[0]
        if(len(temp)>0):
            return [temp.get('label')] + get_citation_levels(temp)
        else:
            return [temp.get('label')]
    perseus_getcap_xml = requests.get(perseus_getcap).text
    root = etree.XML(perseus_getcap_xml.encode('utf-8'))
    ns={'d':'http://chs.harvard.edu/xmlns/cts3/ti'}
    textgroups = root.xpath('//d:textgroup',namespaces=ns)
    nodes = {}
    for tg in textgroups:
        nodes[tg.get('urn')] = {'groupname':tg.xpath('./d:groupname',namespaces=ns)[0].text,'type':'textgroup'}
        works = [work.get('urn') for work in tg.xpath('./d:work',namespaces=ns)]
        for work in tg.xpath('./d:work',namespaces=ns):
            nodes[work.get('urn')] = {'title':work.xpath('./d:title',namespaces=ns)[0].text,'type':'work'}
            editions = [edition.get('urn') for edition in work.xpath('./d:edition ',namespaces=ns)]
            translations = [translation.get('urn') for translation in work.xpath('./d:translation ',namespaces=ns)]
            nodes[work.get('urn')]['versions'] = editions + translations
            for edition in work.xpath('./d:edition ',namespaces=ns):
                citmap = edition.xpath('.//d:citationMapping ',namespaces=ns)
                if(len(citmap)>0):
                    nodes[edition.get('urn')]={'citation_levels':get_citation_levels(citmap[0]),'type':'edition'}
                else:
                    nodes[edition.get('urn')]={'citation_levels':None,'type':'edition'}
            for translation in work.xpath('./d:translation ',namespaces=ns):
                citmap = translation.xpath('.//d:citationMapping ',namespaces=ns)
                if(len(citmap)>0):
                    nodes[translation.get('urn')]={'citation_levels':get_citation_levels(citmap[0]),'type':'translation'}
                else:
                    nodes[translation.get('urn')]={'citation_levels':None,'type':'translation'}
    return nodes
def get_citation_scheme(urn,catalog):
    """
    TODO
    """
    print >> sys.stderr, "found %i versions for %s"%(len(catalog[urn]['versions']),urn)
    longest_scheme = []
    # we now that the Histories are therein contained, but just to be sure...
    if(catalog.has_key(urn)):
        temp = [catalog[version]['citation_levels'] for version in catalog[urn]['versions'] if catalog[version]['citation_levels'] is not None]
        temp = [tuple(x) for x in temp]
        # let's find out what is the longest citation scheme
        # here we assume that the longest is the most canonical
        # in other words, "book/chapter/section" is more canonical than "book/chapter"
        for scheme in set(temp):
            if(len(scheme)>=len(longest_scheme)):
                longest_scheme = scheme
    return list(longest_scheme)
def get_citable_nodes(urn,catalog,scheme,perseus_getvalidreff="http://www.perseus.tufts.edu/hopper/CTS?request=GetValidReff&urn="):
    """
    Explain...

    Returns: 

    {
    u'urn:cts:latinLit:phi0690.phi003:9.99': {'is_first': False,
                                           'is_last': False,
                                           'label': u"P. Vergilius Maro, 'Aeneid': book 9, line 99"}
    , ...
    }

    """
    cts_reply = requests.get(perseus_getvalidreff+"%s"%urn).text
    cts_reply_xml = etree.XML(cts_reply)
    ns={'d':'http://chs.harvard.edu/xmlns/cts3/ti'}
    urns = [CTS_URN(urn.text) for urn in cts_reply_xml.xpath('//d:urn',namespaces=ns)] # strip only the <urn> els
    passage_nodes = {}
    part_of_relations = []
    follow_relations = []
    prev_urn = None
    urn = urns[0]
    work_urn = urn.get_urn_without_passage().replace("."+urn.version,'')
    author_urn = str(urn.get_urn_without_passage().replace("."+urn.work+"."+urn.version,''))
    author = catalog[author_urn]['groupname']
    title = catalog[work_urn]['title']
    for n,urn in enumerate(urns):
        node = {}
        try:
            next_urn = urns[n+1]
        except Exception, e:
            next_urn = None
        if(prev_urn is not None):
            follow_relations.append((str(urn).replace("."+urn.version,''),str(prev_urn).replace("."+urn.version,'')))
        for limit in range(1,urn.get_citation_depth()+1):
            levels = urn.get_passage(limit).split('.')
            label = u"%s, \'%s\': %s"%(author,title,", ".join(["%s %s"%(scheme[n],level) for n,level in enumerate(levels)]))
            urn_no_version = urn.trim_passage(limit).replace("."+urn.version,'')
            if(not passage_nodes.has_key(urn_no_version)):
                passage_nodes[urn_no_version] = {"label":label,"is_first":False,"is_last":False}
                if(CTS_URN(urn.trim_passage(limit)).get_citation_depth()>1):
                    part_of_relations.append((str(urn.trim_passage(limit)).replace("."+urn.version,''),str(urn.trim_passage(limit-1)).replace("."+urn.version,'')))
                    if(prev_urn is not None):
                        try:
                            assert urn.get_passage(limit-1) != prev_urn.get_passage(limit-1)
                            print >> sys.stderr, urn, " is first"
                            passage_nodes[urn_no_version]["is_first"] = True
                            print >> sys.stderr, urn.trim_passage(limit-1), ' follows ',prev_urn.trim_passage(limit-1)
                        except Exception, e:
                            pass
                    if(next_urn is not None):
                        try:
                            assert urn.get_passage(limit-1) != next_urn.get_passage(limit-1)
                            print >> sys.stderr, urn, " is last"
                            passage_nodes[urn_no_version]["is_last"] = True
                        except Exception, e:
                            pass
                    elif(next_urn is None):
                        print >> sys.stderr, urn," is  last"
                        passage_nodes[urn_no_version]["is_last"] = True
                else:
                    pass
        prev_urn = urn
    return passage_nodes, part_of_relations,follow_relations
def main():
    config = ConfigParser.ConfigParser()
    config.readfp(open("agraph.ini"))
    store_params = dict(config.items("surf"))
    store_params['port'] = int(store_params['port']) # force the `port` to be an integer
    s=Store(**store_params)

    """
    s = Store(  reader='rdflib',
                writer='rdflib',
                rdflib_store = 'IOMemory')
    """
    global ss
    ss = surf.Session(s, {})
    print >> sys.stderr, "the 3store contains %s triples"%ss.default_store.size()
    ss.default_store.clear()
    print >> sys.stderr, "the 3store contains %s triples"%ss.default_store.size()
    # define classes
    global Person, Work, Type, TextElement, TextStructure, Identifier
    Person = ss.get_class(surf.ns.EFRBROO['F10_Person'])
    Work = ss.get_class(surf.ns.EFRBROO['F1_Work'])
    Type = ss.get_class(surf.ns.ECRM['E55_Type'])
    TextElement = ss.get_class(surf.ns.HUCIT['TextElement'])
    TextStructure = ss.get_class(surf.ns.HUCIT['TextStructure'])
    Identifier = ss.get_class(surf.ns.ECRM['E42_Identifier'])
    # define the mapping between classes and object definitions
    ss.mapping[surf.ns.EFRBROO.F10_Person] = HucitAuthor
    ss.mapping[surf.ns.EFRBROO.F1_Work] = HucitWork

    catalog = parse_perseus_catalog()
    urns = [
    'urn:cts:latinLit:phi0690.phi003'
    ,'urn:cts:greekLit:tlg0012.tlg001'
    ,'urn:cts:latinLit:phi0690.phi003' 
    ]
    for urn in urns[:1]: # process only the first urn
        longest_scheme = get_citation_scheme(urn,catalog)
        print >> sys.stderr, "*%s* can be cited by %s"%(catalog[urn]['title'],"/".join(longest_scheme))
        passage_nodes, part_of_relations,follow_relations = get_citable_nodes(urn,catalog,longest_scheme)
        passage_nodes = {urn:passage_nodes[urn] for urn in passage_nodes if (CTS_URN(urn).get_passage(1)=="1")}
        print >> sys.stderr, "found %i citable nodes for %s"%(len(passage_nodes),urn)
        text_structure = TextStructure(surf.ns.KB["%s#text_structure"%(urn)])
        text_structure.hucit_is_structure_of = surf.ns.KB["works/%s"%urn]
        text_structure.save()
        levels = [create_text_element_type(Type,level) for level in longest_scheme]
        text_elemements = [create_text_element(TextElement, urn, passage_nodes[urn]["label"],levels[CTS_URN(urn).get_citation_depth()-1],text_structure) for urn in passage_nodes]
        [create_follows_relation(rel) for rel in follow_relations]


    #print data[urn]['follow_relations']
if __name__ == '__main__':
    main()