import re
from typing import Optional, Dict, List, Set, Tuple

from mapping.mapper.base_mapper import Mapper, create_batches, get_prefix
from query_tools import QueryHelper, Query, DBpediaQuery, WikidataQuery, Resource, ResourceError

PROPERTIES_FROM_DBPEDIA_TO_EQUIVALENT = """
SELECT DISTINCT ?resource ?equivalentPredicate ?equivalentResource WHERE {
    ?resource ?equivalentPredicate ?equivalentResource.
    VALUES ?resource { <dbpedia_resources> }
    VALUES ?equivalentPredicate { owl:equivalentProperty owl:equivalentClass }
}
"""
PROPERTIES_FROM_EQUIVALENT_TO_WIKIDATA = """
SELECT DISTINCT ?resource ?equivalentPredicate ?equivalentResource WHERE {
    ?resource ?equivalentPredicate ?equivalentResource.
    VALUES ?equivalentResource { <equivalent_resources> }
    VALUES ?equivalentPredicate { wdt:P1628 wdt:P1709}
}
"""


class PropertiesMapper(Mapper):

    def __init__(self, kb_query: str, map_query: str, kb_placeholder: str, kb_endpoint_url: str, map_endpoint_url: str):
        self.kb_query = kb_query
        self.map_query = map_query
        self.kb_placeholder_pattern = re.compile(kb_placeholder)
        self.eq_placeholder_pattern = re.compile("<equivalent_resources>")
        self.kb_query_helper = QueryHelper(kb_endpoint_url)
        self.map_query_helper = QueryHelper(map_endpoint_url)

    def build_kb_query(self, q_string: str) -> Query:
        return Query(q_string)

    def build_equivalent_query(self, q_string: str) -> Query:
        return Query(q_string)

    def _process_results(self, results: Optional[Dict]) -> List[Dict]:
        if not results:
            return []
        mapped_resources = []
        for result in results["results"]["bindings"]:
            pred_resource = Resource.create_resource(result['resource']['value'])
            try:
                eq_resource = Resource.create_resource(result['equivalentResource']['value'])
            except ResourceError as e:
                print(e)
                continue
            # print(f"({pred_resource}, {eq_resource})")
            mapped_resources.append({
                "resource": pred_resource,
                "equivalentPredicate": result['equivalentPredicate']['value'],
                "equivalentResource": eq_resource
            })
        return mapped_resources

    def map(self, resources: Set[Resource], add_prefixes: bool = False) -> List[Dict]:
        # Get equivalent properties
        resource_list = " ".join({r.get(compress=False) for r in resources})
        query_string = self.kb_placeholder_pattern.sub(resource_list, self.kb_query)
        query = self.build_kb_query(query_string)
        results = self.kb_query_helper.do_query(query, add_prefixes=add_prefixes)
        kb_properties = self._process_results(results)
        # Get mapped properties
        eq_properties_list = " ".join(
            {kb_property['equivalentResource'].get(compress=False) for kb_property in kb_properties
             if not kb_property['equivalentResource'].is_wikidata()})
        eq_query_string = self.eq_placeholder_pattern.sub(eq_properties_list, self.map_query)
        eq_query = self.build_kb_query(eq_query_string)
        results = self.map_query_helper.do_query(eq_query, compressed=False, add_prefixes=add_prefixes)
        map_properties = self._process_results(results)
        results = []
        for kb_property in kb_properties:
            if kb_property['equivalentResource'].is_wikidata():
                _, name = get_prefix(kb_property['equivalentResource'].get())
                results.append({
                    "kb_property": kb_property['resource'],
                    "eq_property": kb_property['equivalentPredicate'],
                    "map_property": Resource.create_resource(f"wdt:{name}")
                    if 'p' in name.lower() else kb_property['equivalentResource']
                })
                continue
            for eq_property in map_properties:
                if kb_property["equivalentResource"] == eq_property["equivalentResource"]:
                    results.append({
                        "kb_property": kb_property["resource"],
                        "eq_property": kb_property["equivalentResource"],
                        "map_property": eq_property["resource"]
                    })
        return results

    def map_resource_batches(
            self,
            properties_to_be_mapped: Set[Resource],
            add_prefixes: bool = False
    ) -> Dict[Resource, List[Tuple[Resource, Resource]]]:
        print("--------------------- PROPERTIES ------------------------")
        print("total properties found:  ", len(properties_to_be_mapped))
        resource_batches = create_batches(list(properties_to_be_mapped))
        mapped_resources = []
        for batch in resource_batches:
            results = self.map(batch, add_prefixes=add_prefixes)
            mapped_resources.extend(results)
        properties_copy = properties_to_be_mapped.copy()
        mapped_properties_dict = {}
        for mapped_property in mapped_resources:
            kb_property = mapped_property['kb_property']
            # check property
            if kb_property in properties_copy:
                properties_copy.remove(kb_property)
            # add new list if not created before
            if kb_property not in mapped_properties_dict:
                mapped_properties_dict[kb_property] = []
            # Fix prefix if name is a property using entity prefix
            _, name = get_prefix(mapped_property['map_property'].get())
            fixed_properties = (
                Resource.create_resource(f"wdt:{name}") if 'p' in name.lower() else mapped_property['map_property']
            )
            # Add map to the map dict
            mapped_properties_dict[kb_property].append((mapped_property['eq_property'], fixed_properties))
            print(mapped_property['kb_property'].get(), mapped_property['map_property'].get())
        print("total properties mapped: ", len(mapped_properties_dict.keys()))
        print("total properties not mapped: ", len(properties_copy))
        return mapped_properties_dict


class MapPropertiesDBpediaToWikidata(PropertiesMapper):

    def __init__(self, kb_endpoint_url: str, map_endpoint_url: str):
        super().__init__(
            PROPERTIES_FROM_DBPEDIA_TO_EQUIVALENT,
            PROPERTIES_FROM_EQUIVALENT_TO_WIKIDATA,
            "<dbpedia_resources>",
            kb_endpoint_url,
            map_endpoint_url
        )

    def build_kb_query(self, q_string: str) -> Query:
        return DBpediaQuery(q_string)

    def build_equivalent_query(self, q_string: str) -> Query:
        return WikidataQuery(q_string)