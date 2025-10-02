# wikidataloader

Easy pythonic wrapper around the [Wikidata SPARQL API](https://query.wikidata.org/) for quick creation of datasets from Wikidata.

Only supports simple, non-recursive queries - for complex queries please directly use the [SPARQL API](https://query.wikidata.org/) provided by Wikidata.

It does not support complex operators (ordering, datetime conversion, string/numeric filtering etc.), because these can be substituted by preprocessing the dataset in Python after retrieval.

## Usage

Look up the URIs for properties (e.g. _P31_) and objects (e.g. _Q5_) on [Wikidata's search engine](https://www.wikidata.org/).

```python
from wikidataloader import WikidataQuery

results = WikidataQuery.search(
    filters={"P31": "Q5", "P27": "Q183", "P106": "Q156839"}, # {is_instance: human, country_of_origin: Germany, profession: cook}
    select=[("P21", "Gender"), ("P19", "City of Birth")],
    limit=30,
	default_language="en"
)

results.to_pandas()

```

For more examples, see [example.ipynb](./example.ipynb)

## Install

Install using pip:

```pip install wikidataloader```

## Limitations

- Does not support recursive queries
- Does not support labels for Lexeme queries
