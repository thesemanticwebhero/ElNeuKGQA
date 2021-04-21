import re
from collections import OrderedDict

from mapping.mapper.base_mapper import get_prefix
from query_tools.dbpedia_utils import DBPEDIA_PREFIXES
from query_tools.wikidata_utils import WIKIDATA_PREFIXES


class ResourceError(Exception):
    pass


class ResourceNotSupportedException(ResourceError):
    pass


class ResourceHelper:

    def __init__(self, short_prefix: str, uri_prefix: str):
        self.__short_prefix = re.compile(f"^{short_prefix}:(\S+)$")
        self.__uri_prefix = re.compile(f"^<?{re.escape(uri_prefix)}([^\s>]+)>?$")

    def get_resource_name(self, name: str) -> str:
        if self.is_compress(name):
            return self.__short_prefix.sub("\g<1>", name)
        elif self.is_decompressed(name):
            return self.__uri_prefix.sub("\g<1>", name)
        else:
            raise ResourceError

    def is_compress(self, name: str) -> bool:
        return self.__short_prefix.search(name) is not None

    def is_decompressed(self, name: str) -> bool:
        return self.__uri_prefix.search(name) is not None


RESOURCES_DICT = OrderedDict()


class Resource:

    def __init__(self, name, short_prefix, uri_prefix):
        self.__short_prefix = short_prefix
        self.__uri_prefix = uri_prefix
        self.__name = ResourceHelper(short_prefix, uri_prefix).get_resource_name(name)

    def get(self, compress: bool = True):
        if compress:
            return "{0}:{1}".format(self.__short_prefix, self.__name)
        else:
            return "<{0}{1}>".format(self.__uri_prefix, self.__name)

    def __eq__(self, other: 'Resource'):
        return self.get(compress=False) == other.get(compress=False)

    def __str__(self):
        return self.get()

    def __hash__(self):
        return hash(self.get(compress=False))

    @classmethod
    def create_resource(cls, resource_uri: str):
        prefix, _ = get_prefix(resource_uri)
        for prefix, ResourceClass in RESOURCES_DICT.items():
            try:
                return ResourceClass(resource_uri)
            except ResourceError:
                pass
        raise ResourceNotSupportedException(f"Resource {resource_uri} not found.")

    def is_wikidata(self):
        return False

    def is_dbpedia(self):
        return False


WIKIDATA_ENTITY_PATTERN = re.compile("(?:wd):(?:[Q|P][\d]+)")
WIKIDATA_PROPERTY_PATTERN = re.compile("(?:wdt|p|ps|pq):(?:P[\d]+)")


class WikidataResource(Resource):

    def is_wikidata(self):
        return True

    def is_entity(self):
        return False


class WikidataEntity(WikidataResource):

    def __init__(self, name):
        key = "wd"
        super().__init__(name, key, WIKIDATA_PREFIXES[key])

    def is_entity(self):
        return True


RESOURCES_DICT["wd"] = WikidataEntity


class WikidataDirectProperty(WikidataResource):

    def __init__(self, name):
        key = "wdt"
        super().__init__(name, key, WIKIDATA_PREFIXES[key])


RESOURCES_DICT["wdt"] = WikidataDirectProperty


class WikidataProperty(WikidataResource):

    def __init__(self, name):
        key = "p"
        super().__init__(name, key, WIKIDATA_PREFIXES[key])


RESOURCES_DICT["p"] = WikidataProperty


class WikidataPropertyStatement(WikidataResource):

    def __init__(self, name):
        key = "ps"
        super().__init__(name, key, WIKIDATA_PREFIXES[key])


RESOURCES_DICT["ps"] = WikidataPropertyStatement


class WikidataPropertyQualifier(WikidataResource):

    def __init__(self, name):
        key = "pq"
        super().__init__(name, key, WIKIDATA_PREFIXES[key])


RESOURCES_DICT["pq"] = WikidataPropertyQualifier


class DBpediaResource(Resource):

    def is_dbpedia(self):
        return True


class DBpediaEntity(DBpediaResource):

    def __init__(self, name):
        key = "dbr"
        super().__init__(name, key, DBPEDIA_PREFIXES[key])


RESOURCES_DICT["dbr"] = DBpediaEntity


class DBpediaAlternativeEntity(DBpediaResource):

    def __init__(self, name):
        key = "res"
        super().__init__(name, key, DBPEDIA_PREFIXES[key])


RESOURCES_DICT["res"] = DBpediaAlternativeEntity


class DBpediaProperty(DBpediaResource):

    def __init__(self, name):
        key = "dbp"
        super().__init__(name, key, DBPEDIA_PREFIXES[key])


RESOURCES_DICT["dbp"] = DBpediaProperty


class DBpediaOntology(DBpediaResource):

    def __init__(self, name):
        key = "dbo"
        super().__init__(name, key, DBPEDIA_PREFIXES[key])


RESOURCES_DICT["dbo"] = DBpediaOntology


class SchemaResource(Resource):

    def __init__(self, name):
        key = "schema"
        super().__init__(name, key, WIKIDATA_PREFIXES[key])


RESOURCES_DICT["schema"] = SchemaResource


class RdfSchemaResource(Resource):

    def __init__(self, name):
        key = "rdfs"
        super().__init__(name, key, WIKIDATA_PREFIXES[key])


RESOURCES_DICT["rdfs"] = RdfSchemaResource


class WikipediaArticle(Resource):

    def __init__(self, name):
        key = "wiki"
        super().__init__(name, key, WIKIDATA_PREFIXES[key])


RESOURCES_DICT["wiki"] = WikipediaArticle


RDFS_PROPERTY_PATTERN = re.compile("rdfs:[\d\w]+")


if __name__ == '__main__':
    compressed_entity = "wd:Q4072104"
    decompressed_entity = "<http://www.wikidata.org/entity/Q4072104>"
    Resource.create_resource(compressed_entity)
    Resource.create_resource(decompressed_entity)
