import re
from typing import Optional, Dict, List, Set, Tuple

from SPARQLWrapper.SPARQLExceptions import QueryBadFormed

from mapping.mapper.base_mapper import Mapper, create_batches, get_prefix
from query_tools import QueryHelper, Query, WikidataQuery, Resource, print_debug

ENTITIES_FROM_WIKIDATA_TO_DBPEDIA = """
SELECT ?article ?wikidata ?dbpedia
WHERE {
    ?article schema:about ?wikidata;
        schema:inLanguage "en" ;
    schema:isPartOf [ wikibase:wikiGroup "wikipedia" ] .
    BIND(IRI(CONCAT("http://dbpedia.org/resource/", SUBSTR(STR(?article),31))) AS ?dbpedia)
    VALUES ?wikidata { <wikidata_entities> }
}
"""
ENTITIES_FROM_DBPEDIA_TO_WIKIDATA = """
SELECT ?article ?wikidata ?dbpedia
WHERE {
    ?article schema:about ?wikidata .
    BIND(IRI(CONCAT("https://en.wikipedia.org/wiki/", SUBSTR(STR(?dbpedia),29))) AS ?article)
    VALUES ?dbpedia { <dbpedia_resources> }
}
"""
ENTITIES_FROM_WIKIPEDIA_TO_WIKIDATA = """
SELECT ?article ?wikidata
WHERE {
    ?article schema:about ?wikidata .
    VALUES ?article { <wikipedia_articles> }
}
"""


class EntityMapperNotImplemented(Exception):
    pass


class EntityMapper(Mapper):

    def __init__(self, map_query: str, placeholder_regex: str, endpoint_url: str, source: str, target: str, compress: bool = True):
        """
        Represent entity mapper from a source KB to a target KB.

        :param map_query: query use to map entities
        :param placeholder_regex: regex string pattern use for identifying placeholder in the map_query
        :param endpoint_url: endpoint url where to execute the mapping process
        """
        self.map_query = map_query
        self.placeholder_pattern = re.compile(placeholder_regex)
        self.query_helper = QueryHelper(endpoint_url)
        self.source = source
        self.target = target
        self.compress = compress

    def build_query(self, query_string: str) -> Query:
        """
        Build a map Query object given a query string.

        :param query_string: query string.
        :return: Query with the given query string.
        """
        raise EntityMapperNotImplemented

    def _process_results(self, results: Optional[Dict]) -> List[Dict]:
        """
        Given a result dictionary from the map query call, parse results to be readable
        to the next process.

        :param results: map query results.
        :return: processed results.
        """
        if not results:
            return []
        mapped_resources = []
        for result in results["results"]["bindings"]:
            _, name = get_prefix(result['article']['value'])
            source_resource = Resource.create_resource(result[self.source]['value'])
            target_resource = Resource.create_resource(result[self.target]['value'])
            mapped_resources.append({
                "article_name": name,
                self.source: source_resource,
                self.target: target_resource
            })
        return mapped_resources

    def map(self, resources: Set[Resource], add_prefixes: bool = False) -> List[Dict]:
        """
        Given a set of entities, do mapping process an return a list of results.

        Output format example:
        [
            {
                'article_name': "https://es.wikipedia.org/wiki/Albert_Einstein",
                'wikidata': "wd:Q937",
                'dbpedia': "dbr:Albert_Einstein"
            }
            ...
        ]

        :param resources: entities to be mapped.
        :param add_prefixes: if True, adds PREFIX statements in the map query.
        :return: list with all the equivalences for each resource.
        """
        resource_list = " ".join([r.get(compress=self.compress) for r in resources])
        query_string = self.placeholder_pattern.sub(resource_list, self.map_query)
        query = self.build_query(query_string)
        try:
            results = self.query_helper.do_query(query, compressed=self.compress, add_prefixes=add_prefixes)
        except QueryBadFormed as e:
            print(e)
            return list()
        return self._process_results(results)

    def map_resource_batches(
            self,
            entities_to_be_mapped: Set[Resource],
            add_prefixes: bool = False
    ) -> Dict[Resource, List[Tuple[Resource, Resource]]]:
        """
        Perform mapping process dividing the resources on batches since the map query can map
        limited number of resources per call.

        Output format example:
        {
            'dbr:Albert_Einstein' : [
                ("https://es.wikipedia.org/wiki/Albert_Einstein", "wd:Q937"), ...
            ]
            ...
        }

        :param entities_to_be_mapped: entities to be divided and mapped.
        :param add_prefixes: if True, adds PREFIX statements in the map query.
        :return: dictionary with all the equivalences for all entities.
        """
        debug = False
        print_debug(debug, "--------------------- ENTITIES ------------------------")
        print_debug(debug, "total entities found:  ", len(entities_to_be_mapped))
        resource_batches = create_batches(list(entities_to_be_mapped))
        mapped_resources = []
        for batch in resource_batches:
            results = self.map(batch, add_prefixes=add_prefixes)
            mapped_resources.extend(results)
        entities_copy = entities_to_be_mapped.copy()
        mapped_entities_dict = {}
        for mapped_entity in mapped_resources:
            entity = mapped_entity[self.source]
            if entity in entities_copy:
                entities_copy.remove(entity)
            if entity not in mapped_entities_dict:
                mapped_entities_dict[entity] = []
            mapped_entities_dict[entity].append((mapped_entity['article_name'], mapped_entity[self.target]))
            print_debug(debug, mapped_entity[self.source].get(), mapped_entity[self.target].get())
        print_debug(debug, "entities mapped: ", " ".join([entity.get() for entity in mapped_entities_dict.keys()]))
        print_debug(debug, "entities not mapped: ", " ".join([entity.get() for entity in entities_copy]))
        print_debug(debug, "total entities mapped: ", len(mapped_entities_dict.keys()))
        print_debug(debug, "total entities not mapped: ", len(entities_copy))
        return mapped_entities_dict


class EntityMapperToWikidata(EntityMapper):

    def build_query(self, query_string: str) -> WikidataQuery:
        """
        Build a map Wikidata Query object given a query string.

        :param query_string: query string.
        :return: Wikidata Query with the given query string.
        """
        return WikidataQuery(query_string)


class MapEntitiesWikidataToDBpedia(EntityMapperToWikidata):

    def __init__(self, endpoint_url: str):
        """
        Represent entity mapper from Wikidata to DBpedia.

        :param endpoint_url: endpoint url where to execute the mapping process
        """
        super().__init__(ENTITIES_FROM_WIKIDATA_TO_DBPEDIA, "<wikidata_entities>", endpoint_url, source='wikidata', target='dbpedia')


class MapEntitiesDBpediaToWikidata(EntityMapperToWikidata):

    def __init__(self, endpoint_url: str):
        """
        Represent entity mapper from DBpedia to Wikidata.

        :param endpoint_url: endpoint url where to execute the mapping process
        """
        super().__init__(ENTITIES_FROM_DBPEDIA_TO_WIKIDATA, "<dbpedia_resources>", endpoint_url, source='dbpedia',
                         target='wikidata', compress=False)


class MapEntitiesWikipediaToWikidata(EntityMapperToWikidata):

    def __init__(self, endpoint_url: str):
        """
        Represent entity mapper from DBpedia to Wikidata.

        :param endpoint_url: endpoint url where to execute the mapping process
        """
        super().__init__(ENTITIES_FROM_WIKIPEDIA_TO_WIKIDATA, "<wikipedia_articles>", endpoint_url, source='article',
                         target='wikidata', compress=False)
