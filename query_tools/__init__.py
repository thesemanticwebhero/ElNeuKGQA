from query_tools.base_query import (
    QueryMethodNotImplemented,
    Query,
    WikidataQuery,
    DBpediaQuery,
    QueryHelper,
    WikidataQueryHelper,
    print_debug,
    add_prefixes,
    compress_sparql,
)
from query_tools.base_tokenizer import Tokenizer, WikidataTokenizer, DBpediaTokenizer
from query_tools.resources import (
    ResourceError,
    ResourceNotSupportedException,
    Resource,
    WikidataResource,
    WikidataEntity,
    WikidataDirectProperty,
    WikidataProperty,
    WikidataPropertyStatement,
    WikidataPropertyQualifier,
    DBpediaResource,
    DBpediaEntity,
    DBpediaAlternativeEntity,
    DBpediaProperty,
    DBpediaOntology,
    SchemaResource,
    RdfSchemaResource,
    WikipediaArticle,
    WIKIDATA_ENTITY_PATTERN,
    WIKIDATA_PROPERTY_PATTERN,
    RDFS_PROPERTY_PATTERN
)
from query_tools.dbpedia_utils import (
    DBPEDIA_ENDPOINT,
    DBPEDIA_REPLACE_RULES,
    DBPEDIA_REGEX_REPLACE_RULES,
    DBPEDIA_REGEX_BACK_REPLACE_RULES,
    DBPEDIA_PREFIXES
)
from query_tools.wikidata_utils import (
    WIKIDATA_ENDPOINT_URL,
    MY_ENDPOINT_URL,
    WIKIDATA_REPLACE_RULES,
    WIKIDATA_REGEX_REPLACE_RULES,
    WIKIDATA_REGEX_BACK_REPLACE_RULES,
    WIKIDATA_PREFIXES
)

__all__ = [
    # base_query
    "QueryMethodNotImplemented",
    "Query",
    "WikidataQuery",
    "DBpediaQuery",
    "QueryHelper",
    "WikidataQueryHelper",
    # base_tokenizer
    "Tokenizer",
    "WikidataTokenizer",
    "DBpediaTokenizer",
    # resources
    "ResourceError",
    "ResourceNotSupportedException",
    "Resource",
    "WikidataResource",
    "WikidataEntity",
    "WikidataDirectProperty",
    "WikidataProperty",
    "WikidataPropertyStatement",
    "WikidataPropertyQualifier",
    "DBpediaResource",
    "DBpediaEntity",
    "DBpediaAlternativeEntity",
    "DBpediaProperty",
    "DBpediaOntology",
    "SchemaResource",
    "RdfSchemaResource",
    "WikipediaArticle",
    # utils
    "WIKIDATA_ENTITY_PATTERN",
    "WIKIDATA_ENDPOINT_URL",
    "DBPEDIA_ENDPOINT",
    "print_debug",
    "add_prefixes",
    "compress_sparql",
]
