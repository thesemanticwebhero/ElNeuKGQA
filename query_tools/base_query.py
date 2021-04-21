import time
from difflib import SequenceMatcher
from urllib.error import HTTPError

from SPARQLWrapper import SPARQLWrapper, JSON

from typing import Optional, Dict, List

from SPARQLWrapper.SPARQLExceptions import QueryBadFormed, EndPointInternalError

from query_tools.resources import *
from query_tools.wikidata_utils import WIKIDATA_PREFIXES, WIKIDATA_ENDPOINT_URL

CONTACT_INFO = ""


# Prints only if debug is True
def print_debug(debug, *args, **kargs):
    if debug:
        print(*args, **kargs)


def add_prefixes(query: str, prefixes: dict= None) -> str:
    """
    Add PREFIX clauses to the SPARQL query string.

    :param query: query string.
    :param prefixes: dictionary with (prefix, uri) data.
    :return: query with PREFIX clauses.
    """
    if not prefixes:
        return query
    prefixes_str = ""
    for prefix, uri in prefixes.items():
        prefixes_str += f"PREFIX {prefix}: <{uri}>\n"
    return prefixes_str + '\n' + query


def compress_sparql(text: str, prefix: str, uri: str) -> str:
    """
    Compress given SPARQL query by replacing all instances of the given uri with the given prefix.

    :param text: SPARQL query to be compressed.
    :param prefix: prefix to use as replace.
    :param uri: uri instance to be replaced.
    :return: compressed SPARQL query.
    """
    bordersremv = lambda matchobj: prefix + ":" + re.sub(f"[<>]|({uri})", "", matchobj.group(0))
    return re.sub(f"<?({uri}).*>?", bordersremv, text)


class QueryMethodNotImplemented(Exception):
    """
    Exception when a Query method has not been implemented.
    """
    pass


class Query:
    """
    Base Class for encapsulating a SPARQL query.
    It allows extracting entities or properties, and querying an SPARQL endpoint,
    """
    def __init__(self, query_string: str, prefixes: Optional[Dict] = None):
        """
        Base Class SPARQL query constructor.

        :param query_string: query string of the Query object.
        :param prefixes: dictionary with uri's prefixes.
        """
        self.query = query_string
        self.prefixes = prefixes if prefixes else OrderedDict()

    def is_compressed(self) -> bool:
        """
        Return True if the query only uses CURIE prefixed entities such as dbr:Narnia or wd:Q5.

        :return: True if query is compressed, False otherwise.
        """
        return re.search(f"<*>", self.query) is None

    def compress(self) -> str:
        """
        Convert all uris on the query to their prefixed representation.
        Ej:
            query (one line) -> "SELECT DISTINCT ?uri WHERE {
                <http://www.wikidata.org/entity/Q4072104> <http://www.wikidata.org/prop/direct/P184> ?uri }"
            compressed query -> "SELECT DISTINCT ?uri WHERE { wd:Q4072104 wdt:P184 ?uri }"

        :return: compressed query string.
        """
        if self.is_compressed():
            return self.query
        query = self.query
        for prefix, uri in self.prefixes.items():
            query = re.sub(f"<{uri}(\S+?)>", f"{prefix}:\g<1>", query)
        return query

    def decompress(self) -> str:
        """
        Convert all prefixed entities on the query to their uri representation.
        Ej:
            query -> "SELECT DISTINCT ?uri WHERE { wd:Q4072104 wdt:P184 ?uri }"
            decompressed query  (one line) -> "SELECT DISTINCT ?uri WHERE {
                <http://www.wikidata.org/entity/Q4072104> <http://www.wikidata.org/prop/direct/P184> ?uri }"

        :return: decompressed query string.
        """
        if not self.is_compressed():
            return self.query
        query = self.query
        for prefix, uri in self.prefixes.items():
            query = re.sub(f"{prefix}:(\S+)", f"<{uri}\g<1>>", query)
        return query

    def _add_prefixes(self, query: str) -> str:
        """
        Add PREFIX clauses to the SPARQL query string.

        :param query: query string.
        :return: query with PREFIX clauses.
        """
        if not self.prefixes:
            return query
        prefixes_str = ""
        for prefix, uri in self.prefixes.items():
            prefixes_str += f"PREFIX {prefix}: <{uri}>\n"
        return prefixes_str + '\n' + query

    def get_query(self, compressed: bool=False, add_prefixes: bool = False) -> str:
        """
        Return query string.

        :param compressed: if True, the query is compressed before returning.
        :param add_prefixes: add CURIE PREFIX clauses if True.
        :return: query string.
        """
        query = self.query
        if compressed:
            query = self.compress()
        if add_prefixes:
            query = self._add_prefixes(query)
        return query.strip()

    def results(self, endpoint: str, compressed: bool = True, add_prefixes: bool = True, agent: str = '') -> Dict:
        """
        Execute the SPARQL query over the given endpoint and return the results.

        :param endpoint: endpoint URL string.
        :param compressed: compress query if True
        :param add_prefixes: add PREFIX statements if True
        :param agent: user policy agent for identification.
        :return: dictionary with the SPARQL query's results.
        """
        debug = False
        # default_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        my_agent = agent if agent else "WikidataQuestionAnswering/0.1 (%s) SPARQLWrapper/1.8.5" % CONTACT_INFO
        sparql = SPARQLWrapper(endpoint, agent=my_agent)
        query = self.get_query(compressed=compressed, add_prefixes=add_prefixes)
        print_debug(debug, query)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        return sparql.query().convert()

    @property
    def entities(self) -> List[Resource]:
        """
        Return the entity resources contained in the SPARQL query.

        :return: list of Resource instances.
        """
        raise QueryMethodNotImplemented

    @property
    def properties(self) -> List[Resource]:
        """
        Return the property resources contained in the SPARQL query.

        :return: list of Resource instances.
        """
        raise QueryMethodNotImplemented

    @property
    def empty_query(self) -> str:
        """
        Return an empty query string, i.e. a query with entities and properties replaced by placeholders.
        Example:
            query       -> "SELECT ?sbj WHERE { wd:Q123 wdt:P106 ?obj . ?obj wdt:P31 wd:Q5 }"
            empty query -> "SELECT ?sbj WHERE { <ent_1> <prop_1> ?obj . ?obj <prop_2> <ent_2> }"

        :return: empty query string.
        """
        empty_query = self.get_query(compressed=True, add_prefixes=False)
        for idx, entity in enumerate(self.entities, 1):
            empty_query = re.sub(str(entity), f"<ent_{idx}>", empty_query)
        for idx, r_property in enumerate(self.properties, 1):
            empty_query = re.sub(str(r_property), f"<prop_{idx}>", empty_query)
        return empty_query

    def is_valid(self) -> bool:
        """
        Check if query string is a valid SPARQL query, i.e. does not contained any placeholder.

        :return:
        """
        return True if not re.search('<[\w_\d]+?>', self.query) else False

    def __str__(self):
        """
        Return string representation.

        :return: SPARQL query string representation.
        """
        return self.get_query(compressed=True)

    def __contains__(self, item: Resource):
        """

        :param item:
        :return:
        """
        return item in self.entities or item in self.properties

    @DeprecationWarning
    def compare(self, query: 'Query') -> float:
        """
        (Deprecated) Compare two queries and return a similarity score.

        :param query: another Query instance.
        :return: similarity float score.
        """
        return SequenceMatcher(None, self.get_query(compressed=True), query.get_query(compressed=True)).ratio()


class WikidataQuery(Query):
    """
    Class that encapsulates a Wikidata SPARQL query.
    """
    def __init__(self, query_string: str):
        """
        Wikidata query class constructor.

        :param query_string: query string of the WikidataQuery object.
        """
        super().__init__(query_string, prefixes=WIKIDATA_PREFIXES)

    @classmethod
    def normalized_query(cls, query_string: str) -> 'WikidataQuery':
        """
        Class method that given a denormalized SPARQL query string, it returns the WikidataQuery representation
        of the normalize representation. The normalization representation avoids any contraction done by using
        the semicolon {;} symbol, thus representing each query triple entirely.
        Example:
            denormalized query -> "SELECT ?obj WHERE { wd:Q123 wdt:P106 wd:Q5 ; wdt:31 ?obj }"
            normalized query   -> "SELECT ?obj WHERE { wd:Q123 wdt:P106 wd:Q5 . wd:Q123 wdt:31 ?obj }"

        :param query_string: denormalized query string.
        :return: normalized WikidataQuery instance.
        """
        query_string = str(cls(query_string))
        COMPRESSED_TRIPLES_PATTERN = (
            re.compile(r"""
            (?P<sbj_1>(?:\?\w+)|(?:wd:Q\d+))    # first subject
            \s+
            (?P<prop_1>\w+:\w+)                 # first property (any type)
            \s+
            (?P<obj_1>(?:\?\w+)|(?:wd:Q\d+))    # first object
            \s+
            ;                                   # second compressed triple
            \s+
            (?P<prop_2>\w+:\w+)                 # second property (any type)
            \s+
            (?P<obj_2>(?:\?\w+)|(?:wd:Q\d+))    # second object
            """, re.X)
        )
        new_sparql = str(query_string)
        while COMPRESSED_TRIPLES_PATTERN.search(new_sparql):
            new_sparql = COMPRESSED_TRIPLES_PATTERN.sub(
                r"\g<sbj_1> \g<prop_1> \g<obj_1> . \g<sbj_1> \g<prop_2> \g<obj_2>", new_sparql)
        return WikidataQuery(new_sparql)

    @property
    def entities(self) -> List[WikidataResource]:
        """
        Return the Wikidata entity resources contained in the SPARQL query.

        :return: list of WikidataResource instances.
        """
        return [Resource.create_resource(entity) for entity in WIKIDATA_ENTITY_PATTERN.findall(self.get_query())]

    @property
    def properties(self) -> List[WikidataResource]:
        """
        Return the Wikidata property resources contained in the SPARQL query.

        :return: list of WikidataResource instances.
        """
        return [Resource.create_resource(w_property) for w_property in
                WIKIDATA_PROPERTY_PATTERN.findall(self.get_query())]


class DBpediaQuery(Query):
    """
    Class that encapsulates a DBpedia SPARQL query.
    """
    def __init__(self, query_string: str):
        """
        DBpediaQuery class constructor.

        :param query_string: query string of the WikidataQuery object.
        """
        super(DBpediaQuery, self).__init__(query_string, prefixes=DBPEDIA_PREFIXES)


class QueryHelper:
    """
    Class helper to execute SPARQL queries with a retry mechanism.
    """
    def __init__(self, endpoint_url: str, sleep_time: int = 60):
        """
        Class QueryHelper constructor.

        :param endpoint_url: url endpoint string where to query.
        :param sleep_time: sleep time between retries.
        """
        self.endpoint = endpoint_url
        self.sleep_time = sleep_time
        self.max_retries = 3

    def do_query(self, query: Query, compressed: bool = True, add_prefixes: bool = False) -> Optional[Dict]:
        """
        Perform query process until it successes or reaches max number of retries.

        :param query: query string
        :param compressed: compress query if True
        :param add_prefixes: add PREFIX statements if True
        :return: query results
        """
        sleep_time = self.sleep_time
        for retry in range(1, self.max_retries + 1):
            try:
                return query.results(self.endpoint, compressed=compressed, add_prefixes=add_prefixes)
            except HTTPError as e:
                print(e)
            except EndPointInternalError as e:
                print(e)
                print(query)
                return None
            except QueryBadFormed as e:
                print("QueryBadFormed: ", query)
                raise e
            sleep_time = retry * sleep_time
            print(f"Retry #{retry} in {sleep_time}s")
            time.sleep(sleep_time)
        print(f"[{self.endpoint}] Max amount of retries ({self.max_retries}) reached!")
        print("query: ", query)
        return None


class WikidataQueryHelper(QueryHelper):
    """
    Class helper to execute SPARQL Wikidata queries with a retry mechanism.

    Uses the Wikidata query service: https://query.wikidata.org/sparql
    """
    def __init__(self, sleep_time: int = 60):
        """
        Class WikidataQueryHelper constructor.

        :param sleep_time: sleep time between retries.
        """
        super().__init__(WIKIDATA_ENDPOINT_URL, sleep_time)