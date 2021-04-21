import unittest

from query_tools.resources import *


class TestResource(unittest.TestCase):

    def auxtestResource(
            self,
            compressed_resource: str,
            decompressed_resource:str,
            resource_1: Resource,
            resource_2: Resource
    ):
        self.assertEqual(resource_1.get(), compressed_resource)
        self.assertEqual(resource_1.get(compress=False), decompressed_resource)
        self.assertEqual(resource_2.get(), compressed_resource)
        self.assertEqual(resource_2.get(compress=False), decompressed_resource)
        self.assertEqual(resource_1, resource_2)

    def testWikidataEntity(self):
        compressed_entity = "wd:Q4072104"
        decompressed_entity = "<http://www.wikidata.org/entity/Q4072104>"
        self.auxtestResource(
            compressed_resource=compressed_entity,
            decompressed_resource=decompressed_entity,
            resource_1=WikidataEntity(compressed_entity),
            resource_2=WikidataEntity(decompressed_entity)
        )
        self.auxtestResource(
            compressed_resource=compressed_entity,
            decompressed_resource=decompressed_entity,
            resource_1=Resource.create_resource(compressed_entity),
            resource_2=Resource.create_resource(decompressed_entity)
        )

    def testWikidataProperty(self):
        compressed_property = "wdt:P184"
        decompressed_property = "<http://www.wikidata.org/prop/direct/P184>"
        self.auxtestResource(
            compressed_resource=compressed_property,
            decompressed_resource=decompressed_property,
            resource_1=WikidataDirectProperty(compressed_property),
            resource_2=WikidataDirectProperty(decompressed_property)
        )
        self.auxtestResource(
            compressed_resource=compressed_property,
            decompressed_resource=decompressed_property,
            resource_1=Resource.create_resource(compressed_property),
            resource_2=Resource.create_resource(decompressed_property)
        )

    def testDBpediaEntity(self):
        compressed_resource = "dbr:Grand_Prix_(Cannes_Film_Festival)"
        decompressed_resource = "<http://dbpedia.org/resource/Grand_Prix_(Cannes_Film_Festival)>"
        self.auxtestResource(
            compressed_resource=compressed_resource,
            decompressed_resource=decompressed_resource,
            resource_1=DBpediaEntity(compressed_resource),
            resource_2=DBpediaEntity(decompressed_resource)
        )
        self.auxtestResource(
            compressed_resource=compressed_resource,
            decompressed_resource=decompressed_resource,
            resource_1=Resource.create_resource(compressed_resource),
            resource_2=Resource.create_resource(decompressed_resource)
        )

    @unittest.expectedFailure
    def testDBpediaAlternativeEntity(self):
        compressed_resource = "res:Game_of_Thrones"
        decompressed_resource = "<http://dbpedia.org/resource/Game_of_Thrones>"
        self.auxtestResource(
            compressed_resource=compressed_resource,
            decompressed_resource=decompressed_resource,
            resource_1=DBpediaAlternativeEntity(compressed_resource),
            resource_2=DBpediaAlternativeEntity(decompressed_resource)
        )
        self.auxtestResource(
            compressed_resource=compressed_resource,
            decompressed_resource=decompressed_resource,
            resource_1=Resource.create_resource(compressed_resource),
            resource_2=Resource.create_resource(decompressed_resource)
        )


    def testDBpediaProperty(self):
        compressed_property = "dbp:equivalentProperty"
        decompressed_property = "<http://dbpedia.org/property/equivalentProperty>"
        self.auxtestResource(
            compressed_resource=compressed_property,
            decompressed_resource=decompressed_property,
            resource_1=DBpediaProperty(compressed_property),
            resource_2=DBpediaProperty(decompressed_property)
        )
        self.auxtestResource(
            compressed_resource=compressed_property,
            decompressed_resource=decompressed_property,
            resource_1=Resource.create_resource(compressed_property),
            resource_2=Resource.create_resource(decompressed_property)
        )


    def testDBpediaOntology(self):
        compressed_ontology = "dbo:award"
        decompressed_ontology = "<http://dbpedia.org/ontology/award>"
        self.auxtestResource(
            compressed_resource=compressed_ontology,
            decompressed_resource=decompressed_ontology,
            resource_1=DBpediaOntology(compressed_ontology),
            resource_2=DBpediaOntology(decompressed_ontology)
        )
        self.auxtestResource(
            compressed_resource=compressed_ontology,
            decompressed_resource=decompressed_ontology,
            resource_1=Resource.create_resource(compressed_ontology),
            resource_2=Resource.create_resource(decompressed_ontology)
        )

    def testResourceEqual(self):
        compressed_entity = Resource.create_resource("wd:Q4072104")
        decompressed_entity = Resource.create_resource("<http://www.wikidata.org/entity/Q4072104>")
        entity_set = {compressed_entity, decompressed_entity}
        self.assertTrue(len(entity_set) == 1)
        resource = entity_set.pop()
        self.assertEqual(str(compressed_entity), str(resource))
        self.assertEqual(str(decompressed_entity), str(resource))

    def testIsWikidata(self):
        wikidata_entity = WikidataEntity("wd:Q4072104")
        wikidata_property = WikidataDirectProperty("wdt:P184")
        self.assertTrue(wikidata_entity.is_wikidata())
        self.assertTrue(wikidata_property.is_wikidata())
        self.assertFalse(wikidata_entity.is_dbpedia())
        self.assertFalse(wikidata_property.is_dbpedia())

    def testIsDBpedia(self):
        dbpedia_resource = DBpediaEntity("dbr:Grand_Prix_(Cannes_Film_Festival)")
        dbpedia_res = DBpediaAlternativeEntity("res:Game_of_Thrones")
        dbpedia_property = DBpediaProperty("dbp:equivalentProperty")
        dbpedia_ontology = DBpediaOntology("dbo:award")
        self.assertTrue(dbpedia_resource.is_dbpedia())
        self.assertTrue(dbpedia_res.is_dbpedia())
        self.assertTrue(dbpedia_property.is_dbpedia())
        self.assertTrue(dbpedia_ontology.is_dbpedia())
        self.assertFalse(dbpedia_resource.is_wikidata())
        self.assertFalse(dbpedia_res.is_wikidata())
        self.assertFalse(dbpedia_property.is_wikidata())
        self.assertFalse(dbpedia_ontology.is_wikidata())


if __name__ == '__main__':
    unittest.main()