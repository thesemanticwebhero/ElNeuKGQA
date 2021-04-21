import unittest

from query_tools.wikidata_utils import WIKIDATA_PREFIXES
from query_tools.base_query import compress_sparql, add_prefixes

query_with_prefixes = """PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX bd: <http://www.bigdata.com/rdf#>


#Gatos
SELECT ?item ?itemLabel 
WHERE 
{
  ?item wdt:P31 wd:Q146.
  ?item rdfs:label ?itemLabel
  FILTER (LANG(?itemLabel) = 'en') .
}
order by ?itemLabel
LIMIT 10000"""

class testSparqlUtils(unittest.TestCase):

    def test(self):
        query_no_prefix = """
#Gatos
SELECT ?item ?itemLabel 
WHERE 
{
  ?item wdt:P31 wd:Q146.
  ?item rdfs:label ?itemLabel
  FILTER (LANG(?itemLabel) = 'en') .
}
order by ?itemLabel
LIMIT 10000"""
        query = "SELECT DISTINCT ?uri WHERE { wd:Q704399 <http://www.wikidata.org/prop/direct/P86> ?uri.}"
        compressed_query = "SELECT DISTINCT ?uri WHERE { wd:Q704399 wdt:P86 ?uri.}"
        entity = "http://www.wikidata.org/prop/direct/P86"
        self.assertEqual(compress_sparql(entity, prefix="wdt", uri=WIKIDATA_PREFIXES["wdt"]), "wdt:P86")
        self.assertEqual(compress_sparql(query, prefix="wdt", uri=WIKIDATA_PREFIXES["wdt"]), compressed_query)
        self.assertEqual(add_prefixes(query_no_prefix, WIKIDATA_PREFIXES), query_with_prefixes)

if __name__ == '__main__':
    unittest.main()