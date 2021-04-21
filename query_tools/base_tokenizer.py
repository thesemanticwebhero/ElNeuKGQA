import re
from typing import Optional, Dict

from query_tools.base_query import Query, WikidataQuery, DBpediaQuery
from query_tools.dbpedia_utils import DBPEDIA_REPLACE_RULES, DBPEDIA_REGEX_BACK_REPLACE_RULES
from query_tools.wikidata_utils import WIKIDATA_REPLACE_RULES, WIKIDATA_REGEX_REPLACE_RULES, WIKIDATA_REGEX_BACK_REPLACE_RULES


class TokenizerMethodNotImplemented(Exception):
    """
    Exception when a Tokenizer method has not been implemented.
    """
    pass


class Tokenizer:
    """
    Tokenizer base class for encoding and decoding SPARQL queries for the Query Generator model.
    """
    def __init__(self, replace_rules: Optional[Dict] = None, regex_rules: Optional[Dict] = None,
                 regex_back_rules: Optional[Dict] = None):
        """
        Base Tokenizer class constructor.

        :param replace_rules: replace rules for tokenizing.
        :param regex_rules: regex rules to encode query.
        :param regex_back_rules: regex rules to decode query.
        """
        self.rules = replace_rules if replace_rules else dict()
        self.regex_rules = regex_rules if regex_rules else dict()
        self.regex_back_rules = regex_back_rules if regex_back_rules else dict()

    def encode(self, query: Query) -> str:
        """
        Transform a SPARQL query to a tokenized query string. Compress the query if not compressed.
        Ej:
            query -> "SELECT DISTINCT ?uri WHERE { wd:Q4072104 wdt:P184 ?uri }"
            tokenize query -> "select distinct var_uri where brack_open wd_q4072104 wdt_p184 var_uri brack_close"

        :param query: Query instance.
        :return: encoded string query.
        """
        q_string = query.get_query(compressed=True).lower()
        for pattern, replace in self.regex_rules.items():  # iterating through keys
            q_string = re.sub(pattern, replace, q_string)  # re.sub(rule, key, q_string)
        for key, rule in self.rules.items():  # iterating through keys
            q_string = q_string.replace(rule, key)
        return q_string.strip()

    def decode(self, query_string: str) -> Query:
        """
        Transform a tokenized query string to a SPARQL query. It assumes that the query is tokenize.
        Perform correction if needed.
        Ej:
            tokenize query -> "select distinct var_uri where brack_open wd_q4072104 wdt_p184 var_uri brack_close"
            query -> "SELECT DISTINCT ?uri WHERE { wd:q4072104 wdt:p184 ?uri }"

        :param query_string: encoded string query.
        :return: Query instance.
        """
        q_string = query_string
        for pattern, replace in self.regex_back_rules.items():  # iterating through keys
            q_string = re.sub(pattern, replace, q_string)  # re.sub(rule, key, q_string)
        for key, rule in self.rules.items():  # iterating through keys
            q_string = re.sub(key, rule, q_string)  # perform the S&R
        return self._correction(q_string)

    def _correction(self, query_string: str) -> Query:
        """
        Fix query and return Query object.

        :param query_string: query string to be corrected.
        :return: Query instance.
        """
        return Query(query_string)


class WikidataTokenizer(Tokenizer):
    """
    Tokenizer class for encoding and decoding SPARQL Wikidata queries for the Query Generator model.
    """
    def __init__(self):
        """
        WikidataTokenizer class constructor.
        """
        super().__init__(replace_rules=WIKIDATA_REPLACE_RULES, regex_rules=WIKIDATA_REGEX_REPLACE_RULES,
                         regex_back_rules=WIKIDATA_REGEX_BACK_REPLACE_RULES)

    def _correction(self, query_string: str) -> WikidataQuery:
        """
        Fix query by applying upper function to Q and P Wikidata entities.

        :param query_string: query string to be corrected.
        :return: WikidataQuery instance.
        """
        query_string = re.sub(r"\b(\w+):q(\d+)\b", r"\1:Q\2", query_string)
        query_string = re.sub(r"\b(\w+):p(\d+)\b", r"\1:P\2", query_string)
        query_string = re.sub(r"\s{2,}", ' ', query_string)
        return WikidataQuery(query_string)


class DBpediaTokenizer(Tokenizer):
    """
    Tokenizer class for encoding and decoding SPARQL DBpedia queries for the Query Generator model.
    """
    def __init__(self):
        """
        DBpediaTokenizer class constructor.
        """
        super(DBpediaTokenizer, self).__init__(replace_rules=DBPEDIA_REPLACE_RULES,
                                               regex_rules=DBPEDIA_REGEX_BACK_REPLACE_RULES,
                                               regex_back_rules=DBPEDIA_REGEX_BACK_REPLACE_RULES)

    def _correction(self, query_string: str) -> DBpediaQuery:
        """
        Fix query by applying upper function to Q and P DBpedia entities.

        :param query_string: query string to be corrected.
        :return: DbpediaQuery instance
        """
        # q_string = re.sub(r"\b(\w+):q(\d+)\b", r"\1:Q\2", q_string)
        # q_string = re.sub(r"\b(\w+):p(\d+)\b", r"\1:P\2", q_string)
        return DBpediaQuery(query_string)