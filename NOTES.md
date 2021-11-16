```
%load_ext autoreload
%autoreload 2
import surf
from knowledge_base import KnowledgeBase
kb = KnowledgeBase("../../knowledge_base/config/virtuoso_local.ini")
w = kb.get_resource_by_urn("urn:cts:greekLit:tlg0012.tlg001")
ts = w.add_text_structure("Canonical text structure of homer's iliad")
w.remove_text_structure(ts)

te = kb._session.get_resource("%s/urn:cts:greekLit:tlg0012.tlg001:1" % w.subject
                              , kb._session.get_class(surf.ns.HUCIT['TextElement']))
```

**TODO**:

- [x] refactor sub-module names/organisation
- [ ] fix bug in `surf` query translator (see below)
- [ ] merge epibau branch
- [ ] attach TextElements to a named graph, named after the TextStructure they live in (its URI)
- [ ] tests for the populate module
- [ ] in travis, run tests against the newly installed triple store (not the remote one)

**bug with `surf`**

problem: when calling `surf.resource.Resource.update()` the `language` of `Literal`
gets overwritten to `None`.

this is what the log (of the underlying SPARQL query) looks like:

```
2020-10-02 11:09:52,440 DEBUG    surf    DELETE  FROM <http://purl.org/hucit/kb> {  ?s ?p ?o  } WHERE { {  {  ?s ?p ?o .  FILTER (?s = <http://purl.org/hucit/kb/authors/937/name> AND ?p = <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>)  }  } UNION {  {  ?s ?p ?o .  FILTER (?s = <http://purl.org/hucit/kb/authors/937/name> AND ?p = <http://www.w3.org/2000/01/rdf-schema#label>)  }  } }
2020-10-02 11:09:52,477 DEBUG    surf    INSERT  INTO <http://purl.org/hucit/kb> {  <http://purl.org/hucit/kb/authors/937/name> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://erlangen-crm.org/efrbroo/F12_Name> .  <http://purl.org/hucit/kb/authors/937/name> <http://www.w3.org/2000/01/rdf-schema#label> "Isaeus" .  <http://purl.org/hucit/kb/authors/937/name> <http://www.w3.org/2000/01/rdf-schema#label> "Isaios" .  <http://purl.org/hucit/kb/authors/937/name> <http://www.w3.org/2000/01/rdf-schema#label> "Iseo" .  <http://purl.org/hucit/kb/authors/937/name> <http://www.w3.org/2000/01/rdf-schema#label> "Isée"  }
```

This seems related to this line of the SPARQL query translator: https://github.com/franzlst/surfrdf/blob/ba1024c5efbee68cda24b3120de986ccdb8defab/surf/query/translator/sparql.py#L96 as `isinstance(name.rdfs_label.first, str)` return `True`, thus when translating a `Literal` the correct if/else
statement is not triggered.

possible solution: swap lines 96 and 103

when doing this, make sure to clone from https://github.com/franzlst/surfrdf
I may also try to get in touch with him mail@franzsteinmetz.de

---------------

.. note::
    Notes on fetching less common/stable text structures (Bekker, Stephanus).

    **Problem**: the Leipzig CTS API exposes only Stephanus pages (e.g. 17)
                but not Stephanus sections (e.g. 17a). but the sections are there
                in the TEI XML, marked up as `tei"milestone` elements.

    **Solution**: a solution to this is to fetch the first level via the API,
                and extract the second level units directly from the TEI/XML
                via xpath.

    `resolver.getPassage()\
    .export(output=Mimetypes.PYTHON.ETREE).xpath(".//tei:milestone")` ecc


## Publish library to pypi.org

```
python setup.py sdist

twine check dist/*

twine upload dist/*
```

