import requests
import pandas as pd

class WikidataQuery:
    def __init__(self, query: str, _df: str):
        self.query: str = query
        self._df: pd.DataFrame = _df

    @classmethod
    def search(cls, filters: dict, select: list[str, str], default_language: str = "[AUTO_LANGUAGE]", limit: int | None = None):
        if not filters:
            raise ValueError("No features provided for 'filters'.")

        sparql_query = []

        # SELECT
        select_statement = "SELECT DISTINCT ?itemLabel "
        for _, select_column_name in select:
            select_statement += f"?{select_column_name.replace(' ', '_')}Label "
        sparql_query.append(select_statement)

        # WHERE
        where_statement = "WHERE{\n"

        for filter_property, filter_value in filters.items():
            where_statement += f"?item wdt:{filter_property} wd:{filter_value} .\n"
        
        for select_property, select_column_name in select:
            where_statement += "OPTIONAL{?item wdt:" + select_property + " ?" + select_column_name.replace(' ', '_') + " .}\n"
        
        where_statement += 'SERVICE wikibase:label { bd:serviceParam wikibase:language "' + default_language + ',[AUTO_LANGUAGE],mul,fr,ar,be,bg,bn,ca,cs,da,de,el,en,es,et,fa,fi,he,hi,hu,hy,id,it,ja,jv,ko,nb,nl,eo,pa,pl,pt,ro,ru,sh,sk,sr,sv,sw,te,th,tr,uk,yue,vec,vi,zh". }\n'
        where_statement += "}\n"
        sparql_query.append(where_statement)

        # LIMIT
        if not limit is None:
            sparql_query.append(f"LIMIT {limit}")

        sparql_query_str = "\n".join(sparql_query)
        _df = cls._retrieve_from_wikidata(sparql_query_str)
        _df.columns = [col[:-5] if col.endswith("Label") else col for col in _df.columns] # remove artifact in column names left by wikibase label service

        return cls(query = sparql_query_str, _df = _df)

    @classmethod
    def from_sparql_query(cls, sparql_query: str):
        _df = cls._retrieve_from_wikidata(sparql_query)
        return cls(query = sparql_query, _df = _df)

    def to_pandas(self):
        return self._df

    def to_hf_dataset(self):
        try:
            from datasets import Dataset
            return Dataset.from_pandas(self._df)
        except ModuleNotFoundError:
            raise ModuleNotFoundError("Could not convert: datasets not installed")

    def to_polars(self):
        try:
            import polars
            return polars.from_pandas(self._df)
        except ModuleNotFoundError:
            raise ModuleNotFoundError("Could not convert: polars not installed")

    @staticmethod
    def _retrieve_from_wikidata(sparql_query: str) -> pd.DataFrame:
        headers = { 'Accept': 'application/sparql-results+json' }
        params = {'query': sparql_query}
        response = requests.get("https://query.wikidata.org/sparql", headers=headers, params=params).json()


        # parse nested json response to list of dicts
        column_names = response["head"]["vars"]

        data = []
        for row in response["results"]["bindings"]:
            row_item = {col: row.get(col, {}).get('value', None) for col in column_names}
            data.append(row_item)

        return pd.DataFrame(data)

    def __repr__(self):
        return self._df.__repr__() + "(Wikidata Results)"

