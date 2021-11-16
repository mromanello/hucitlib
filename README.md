# HuCit Knowledge Base

## Status

[![PyPI version](https://badge.fury.io/py/hucitlib.svg)](https://badge.fury.io/py/hucitlib)
[![Build Status](http://img.shields.io/travis/mromanello/hucit_kb.svg)](https://travis-ci.org/mromanello/hucit_kb)
[![codecov](https://codecov.io/gh/mromanello/hucit_kb/branch/master/graph/badge.svg)](https://codecov.io/gh/mromanello/hucit_kb)

**NB:** `hucitlib` is currently being ported from Python 2 to 3. For legacy-related
reasons, the version available on PyPi (`hucitlib 0.2.9`) still supports only Python 2.
If you need Python 3 support you may want to install version `0.3.0` available in the [issue-3/py3 branch](https://github.com/mromanello/hucit_kb/tree/issue-3/py3) (you will need to install
it from sources as it currently requires a forked version of `surf`, since the official `surf` does not support Python 3 yet).

## Description

The HuCit KB is a knowledge base about classical (Greek and Latin) texts, developed with the precise aim of supporting the automatic extraction of bibliographic references to such texts.

The data model of the HuCit KB is based on the following ontologies:

* [CIDOC-CRM](http://www.cidoc-crm.org/)
* [FRBRoo](http://www.cidoc-crm.org/frbroo/)
* [HuCit](http://www.essepuntato.it/lode/owlapi/http://purl.org/net/hucit)

It builds upon and connects with the following resources:

* [Classical Works Knowledge Base](http://cwkb.org/linkedopendata)
* [Perseus Catalog](http://catalog.perseus.org)
* [Perseus Digital Library](http://perseus.tufts.edu)
* [Wikidata](http://wikidata.org)
* [VIAF](http://viaf.org)

## Installation

    git clone https://github.com/mromanello/hucit_kb.git
    cd hucit_kb
    python setup.py install

Or via `pip`:

    pip install hucitlib

## Command Line

The library comes with a (development) Command Line Interface.

To see the documentation, try running:

    hucit --help

For example, you can search works by name:

    hucit find "Iliad"

or look up authors/works by CTS URNs:

    hucit find urn:cts:greekLit:tlg0012.tlg001

## Stats

### Basic stats

|                      |   Total |   Min |   Max |     Mean |   Variance |
|:---------------------|--------:|------:|------:|---------:|-----------:|
| Author names         |    4842 |     1 |    27 | 3.12791  |   9.81298  |
| Author abbreviations |     774 |     0 |     2 | 0.5      |   0.26309  |
| Work titles          |   10354 |     1 |    31 | 1.99154  |   6.4174   |
| Work abbreviations   |    2377 |     0 |     3 | 0.457203 |   0.574496 |

### LOD stats

|         |   link to Perseus Catalog (%) |   link to CWKB (%) |   link to VIAF (%) |   link to Wikidata (%) |
|:--------|-------------------------------:|--------------------:|--------------------:|------------------------:|
| Authors |                           4.91 |              100.00 |                5.88 |                    4.91 |

## Example

This is an example of how to use the HuCit KB programmatically:

```python

>>> import pprint
>>> import pkg_resources
>>> from knowledge_base import KnowledgeBase

>>> virtuoso_cfg_file = pkg_resources.resource_filename('knowledge_base','config/virtuoso.ini')

>>> kb = KnowledgeBase(virtuoso_cfg_file)

>>> search_results = kb.search('Omero')

>>> print result.to_json()
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
    {
      "urn": "urn:cts:greekLit:tlg0012.tlg002",
      "titles": [
        {
          "language": "en",
          "label": "Odyssey"
        },
        {
          "language": "de",
          "label": "Odyssee"
        },
        {
          "language": "la",
          "label": "Odyssea"
        },
        {
          "language": "fr",
          "label": "l'Odyss\u00e9e"
        },
        {
          "language": "it",
          "label": "Odissea"
        }
      ],
      "uri": "http://purl.org/hucit/kb/works/2816",
      "title_abbreviations": [
        "Od.",
        "Odyss."
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
      "uri": "http://purl.org/hucit/kb/works/2814",
      "title_abbreviations": [
        "epigr."
      ]
    }
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
```

