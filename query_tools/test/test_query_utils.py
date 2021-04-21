import unittest

from query_tools.base_tokenizer import WikidataTokenizer, DBpediaTokenizer
from query_tools.base_query import WikidataQuery
from templates.wikidata_template import WikidataTemplate


class TestQuery(unittest.TestCase):

    def testWikidataQuery(self):
        query_1 = "SELECT DISTINCT ?uri WHERE { <http://www.wikidata.org/entity/Q4072104> <http://www.wikidata.org/prop/direct/P184> ?uri }"
        compressed_query_1 = "SELECT DISTINCT ?uri WHERE { wd:Q4072104 wdt:P184 ?uri }"
        q1 = WikidataQuery(query_1)
        cq1 = WikidataQuery(compressed_query_1)
        self.assertFalse(q1.is_compressed())
        self.assertTrue(cq1.is_compressed())
        self.assertEqual(q1.compress(), cq1.get_query())
        self.assertEqual(cq1.decompress(), q1.get_query())

class TestTokenizer(unittest.TestCase):

    def testWikidataTokenizer(self):
        tokenizer = WikidataTokenizer()

        q1 = WikidataQuery("SELECT DISTINCT ?uri WHERE { <http://www.wikidata.org/entity/Q4072104> <http://www.wikidata.org/prop/direct/P184> ?uri }")
        cq1 = WikidataQuery("SELECT DISTINCT ?uri WHERE { wd:Q4072104 wdt:P184 ?uri }")
        encoded_query_1 = "select distinct var_uri where brack_open wd_q4072104 wdt_p184 var_uri brack_close"
        self.assertEqual(tokenizer.encode(q1), encoded_query_1)
        self.assertEqual(tokenizer.encode(cq1), encoded_query_1)
        decoded_query_1 = "select distinct ?uri where { wd:Q4072104 wdt:P184 ?uri }"
        self.assertEqual(tokenizer.decode(encoded_query_1).get_query(), decoded_query_1)

        encoded_query_2 = "select distinct var_uri where brack_open wd_q3025443 wdt_p86 var_uri brack_close"
        decoded_query_2 = "select distinct ?uri where { wd:Q3025443 wdt:P86 ?uri }"
        self.assertEqual(tokenizer.decode(encoded_query_2).get_query(), decoded_query_2)

        query_3 = "SELECT ?value WHERE { <x> p:P2128 ?s . ?s ps:P2128 ?x filter(contains(?x,'162.0')) . ?s pq:P459 ?value}"
        encoded_query_3 = "select var_value where brack_open placeholder_x p_p2128 var_s sep_dot var_s ps_p2128 var_x filter attr_open contains attr_open var_x sep_comma apstrph_162_dot_0_apstrph attr_close attr_close sep_dot var_s pq_p459 var_value brack_close"
        decoded_query_3 = "select ?value where { <x> p:P2128 ?s . ?s ps:P2128 ?x filter ( contains ( ?x , '162.0' ) ) . ?s pq:P459 ?value }"
        q3 = WikidataQuery(query_3)
        self.assertEqual(encoded_query_3, tokenizer.encode(q3))
        self.assertEqual(tokenizer.decode(encoded_query_3).get_query(), decoded_query_3)

        query_string_4 = "ASK WHERE { wd:Q658 wdt:P1108 ?obj filter(?obj < 1.2) }"
        query_4 = WikidataQuery(query_string_4)
        encoded_query_4 = "ask where brack_open wd_q658 wdt_p1108 var_obj filter attr_open var_obj math_lt 1_dot_2 attr_close brack_close"
        decoded_query_4 = "ask where { wd:Q658 wdt:P1108 ?obj filter ( ?obj < 1.2 ) }"
        self.assertEqual(tokenizer.encode(query_4), encoded_query_4)
        self.assertEqual(tokenizer.decode(encoded_query_4).get_query(), decoded_query_4)

    def testWikidataTokenizerWithStringCases(self):
        tokenizer = WikidataTokenizer()

        query_string_5 = "SELECT DISTINCT ?sbj ?sbj_label WHERE { ?sbj wdt:P31 wd:Q427626 . ?sbj rdfs:label ?sbj_label . FILTER(CONTAINS(lcase(?sbj_label), 'variety')) . FILTER (lang(?sbj_label) = 'en') } LIMIT 25"
        query_5 = WikidataQuery(query_string_5)
        encoded_query_5 = "select distinct var_sbj var_sbj_label where brack_open var_sbj wdt_p31 wd_q427626 sep_dot var_sbj rdfs_label var_sbj_label sep_dot filter attr_open contains attr_open lcase attr_open var_sbj_label attr_close sep_comma apstrph_variety_apstrph attr_close attr_close sep_dot filter attr_open lang attr_open var_sbj_label attr_close math_eq apstrph_en_apstrph attr_close brack_close limit 25"
        decoded_query_5 = "select distinct ?sbj ?sbj_label where { ?sbj wdt:P31 wd:Q427626 . ?sbj rdfs:label ?sbj_label . filter ( contains ( lcase ( ?sbj_label ) , 'variety' ) ) . filter ( lang ( ?sbj_label ) = 'en' ) } limit 25"
        self.assertEqual(encoded_query_5, tokenizer.encode(query_5))
        self.assertEqual(decoded_query_5, tokenizer.decode(encoded_query_5).get_query())

        query_string_6 = WikidataTemplate(query_string_5).get_query_template(query_5)
        query_6 = WikidataQuery(query_string_6)
        encoded_query_6 = "select distinct var_sbj var_sbj_label where brack_open var_sbj wdt_p31 placeholder_obj_1 sep_dot var_sbj rdfs_label var_sbj_label sep_dot filter attr_open contains attr_open lcase attr_open var_sbj_label attr_close sep_comma placeholder_str_value attr_close attr_close sep_dot filter attr_open lang attr_open var_sbj_label attr_close math_eq apstrph_en_apstrph attr_close brack_close limit 25"
        decoded_query_6 = "select distinct ?sbj ?sbj_label where { ?sbj wdt:P31 <obj_1> . ?sbj rdfs:label ?sbj_label . filter ( contains ( lcase ( ?sbj_label ) , <str_value> ) ) . filter ( lang ( ?sbj_label ) = 'en' ) } limit 25"
        self.assertEqual(encoded_query_6, tokenizer.encode(query_6))
        self.assertEqual(decoded_query_6, tokenizer.decode(encoded_query_6).get_query(), )

    def testDBpediaTokenizer(self):
        encoded_query = "SELECT DISTINCT var_uri where brack_open dbr_Mad_River_ attr_open California attr_close  dbo_city var_uri brack_close"
        encoded_query_2 = "ask where brack_open dbr_Island_Barn_Reservoir dbo_areaTotal var_a1 sep_dot dbr_Arab_League dbo_areaTotal var_a2 sep_dot filter  attr_open var_a1math_gtvar_a2 attr_close  brack_close"
        encoded_query_3 = "SELECT DISTINCT COUNT attr_open var_uri attr_close  where brack_open var_uri dbp_distributor dbr_Electronic_Arts brack_close"
        encoded_query_4 = "SELECT DISTINCT var_uri where brack_open dbr_Up_All_Night_ attr_open One_Direction_album attr_close  dbp_writer var_uri sep_dot dbr_Air_Guitar_ attr_open McBusted_song attr_close  dbo_writer var_uri brack_close"
        encoded_query_5 = "SELECT DISTINCT COUNT attr_open var_uri attr_close  where brack_open var_x dbo_builder dbr_Department_of_Public_Works_and_Highways_ attr_open Philippines attr_close  sep_dot var_x dbo_builder var_uri brack_close"
        encoded_query_6 = "SELECT DISTINCT COUNT attr_open var_uri attr_close  where brack_open var_x dbo_team dbr_İzmir_Büyükşehir_Belediyesi_GSK_ attr_open men's_ice_hockey attr_close  sep_dot var_x dbo_formerTeam var_uri sep_dot var_uri a dbo_SportsTeam brack_close"
        encoded_query_7 = "SELECT DISTINCT var_uri where brack_open var_x dbo_hometown dbr_Île-de-France_ attr_open region attr_close  sep_dot var_x dbp_genre var_uri sep_dot var_x a dbo_Band brack_close"
        encoded_query_8 = "SELECT DISTINCT var_uri where brack_open dbr_ZFS_ attr_open z/OS_file_system attr_close  dbp_developer var_uri sep_dot dbr_Maqetta dbo_author var_uri brack_close"
        encoded_query_9 = "select distinct var_uri where brack_open brack_open var_uri dbo_field dbr_Jazz sep_dot brack_close union brack_open var_uri dc:description var_s sep_dot filter regex attr_open var_s,'dbr_Jazz','i' attr_close  brack_close var_uri dbo_award dbr_Academy_Awards sep_dot brack_close"
        encoded_query_10 = "ASK where brack_open dbr_ attr_open 12538 attr_close _1998_OH dbo_discoverer dbr_Near_Earth_Asteroid_Tracking brack_close"
        encoded_query_11 = "ask where brack_open dbr_Alexis_Denisof dbo_spouse var_spouse sep_dot var_spouse rdfs_label var_name sep_dot filter attr_open regex attr_open var_name,'dbo_Station' attr_close  attr_close  brack_close"
        tokenizer = DBpediaTokenizer()
        print(tokenizer.decode(encoded_query).get_query(add_prefixes=False))
        print(tokenizer.decode(encoded_query_2).get_query(add_prefixes=False))
        print(tokenizer.decode(encoded_query_3).get_query(add_prefixes=False))
        print(tokenizer.decode(encoded_query_4).get_query(add_prefixes=False))
        print(tokenizer.decode(encoded_query_5).get_query(add_prefixes=False))
        print(tokenizer.decode(encoded_query_6).get_query(add_prefixes=False))
        print(tokenizer.decode(encoded_query_7).get_query(add_prefixes=False))
        print(tokenizer.decode(encoded_query_8).get_query(add_prefixes=False))
        print(tokenizer.decode(encoded_query_9).get_query(add_prefixes=False))
        print(tokenizer.decode(encoded_query_10).get_query(add_prefixes=False))
        print(tokenizer.decode(encoded_query_11).get_query())

if __name__ == '__main__':
    unittest.main()