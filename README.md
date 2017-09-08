# A HuCit Knowledge Base

## Status

[![Build Status](http://img.shields.io/travis/mromanello/hucit_kb.svg)](https://travis-ci.org/mromanello/hucit_kb)
[![codecov](https://codecov.io/gh/mromanello/hucit_kb/branch/master/graph/badge.svg)](https://codecov.io/gh/mromanello/hucit_kb)

## Description



Based on the [HuCit Ontology](http://www.essepuntato.it/lode/owlapi/http://purl.org/net/hucit).


## Stats

### Basic stats

|                      |   Total |   Min |   Max |     Mean |   Variance |
|:---------------------|--------:|------:|------:|---------:|-----------:|
| Author names         |    4842 |     1 |    27 | 3.12791  |   9.81298  |
| Author abbreviations |     774 |     0 |     2 | 0.5      |   0.26309  |
| Work titles          |   10354 |     1 |    31 | 1.99154  |   6.4174   |
| Work abbreviations   |    2377 |     0 |     3 | 0.457203 |   0.574496 |
### LOD stats

TODO

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
