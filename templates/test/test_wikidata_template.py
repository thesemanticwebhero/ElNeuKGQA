import unittest
from typing import Dict

from templates.wikidata_template import WikidataTemplate, WikidataQueryFixer


class TestWikidataTemplate(unittest.TestCase):

    def aux_test_empty_query(self, query_string: str, expected_template: str, **kwargs):
        template = WikidataTemplate(query_string)
        self.assertEqual(template.get_empty_query(**kwargs), expected_template)

    def aux_test_base_template(self, query_string: str, expected_template: str):
        template = WikidataTemplate(query_string)
        self.assertEqual(template.get_base_template(), expected_template)

    def aux_test_get_slots(self, query_string: str, expected_slots: Dict):
        template = WikidataTemplate(query_string)
        self.assertEqual(template.get_slots(), expected_slots)

    def test_empty_query_with_numbers(self):
        self.aux_test_empty_query(
            query_string="ASK WHERE { wd:Q650 wdt:P2102 ?obj filter(?obj = 307) }",
            expected_template="ASK WHERE { <sbj_1> wdt:P2102 ?obj filter(?obj = <num>) }"
        )
        self.aux_test_empty_query(
            query_string="ASK WHERE { wd:Q650 wdt:P2102 ?obj filter(?obj < -307) }",
            expected_template="ASK WHERE { <sbj_1> wdt:P2102 ?obj filter(?obj < <num>) }"
        )
        self.aux_test_empty_query(
            query_string="ASK WHERE { wd:Q650 wdt:P2102 ?obj filter(?obj > 1.2) }",
            expected_template="ASK WHERE { <sbj_1> wdt:P2102 ?obj filter(?obj > <num>) }"
        )
        self.aux_test_empty_query(
            query_string="ASK WHERE { wd:Q650 wdt:P2102 ?obj filter(?obj = -1.2) }",
            expected_template="ASK WHERE { <sbj_1> wdt:P2102 ?obj filter(?obj = <num>) }"
        )
        self.aux_test_empty_query(
            query_string="ASK WHERE { wd:Q650 wdt:P2102 ?obj filter(?obj < 1e+10) }",
            expected_template="ASK WHERE { <sbj_1> wdt:P2102 ?obj filter(?obj < <num>) }"
        )
        self.aux_test_empty_query(
            query_string="ASK WHERE { wd:Q650 wdt:P2102 ?obj filter(?obj > 1.7e-10) }",
            expected_template="ASK WHERE { <sbj_1> wdt:P2102 ?obj filter(?obj > <num>) }"
        )
        self.aux_test_empty_query(
            query_string="ASK WHERE { wd:Q650 wdt:P2102 ?obj filter(?obj = t12341231) }",
            expected_template="ASK WHERE { <sbj_1> wdt:P2102 ?obj filter(?obj = <num>) }"
        )

    def test_get_slots(self):
        query_string_1 = "SELECT DISTINCT ?uri WHERE { ?uri  wdt:P106 wd:Q11631 . { ?uri wdt:P27 wd:Q15180 } UNION { ?uri wdt:P27 wd:Q159 } }"
        self.aux_test_get_slots(
            query_string=query_string_1,
            expected_slots={'wd:Q11631': '<obj_1>', 'wd:Q15180': '<obj_2>', 'wd:Q159': '<obj_3>'}
        )
        self.aux_test_empty_query(
            query_string=query_string_1,
            expected_template="SELECT DISTINCT ?uri WHERE { ?uri  wdt:P106 <obj_1> . { ?uri wdt:P27 <obj_2> } UNION { ?uri wdt:P27 <obj_3> } }"
        )
        query_string_2 = "SELECT DISTINCT ?uri WHERE {  wd:Q5620660 ^pq:P453/ps:P161 ?uri }"
        self.aux_test_get_slots(
            query_string=query_string_2,
            expected_slots={'wd:Q5620660': '<sbj_1>'}
        )
        self.aux_test_empty_query(
            query_string=query_string_2,
            expected_template="SELECT DISTINCT ?uri WHERE {  <sbj_1> ^pq:P453/ps:P161 ?uri }"
        )

    def test_sparql_template_base_template(self):
        query_string = "select distinct ?sbj where { ?sbj wdt:P1376 wd:Q1195 . ?sbj wdt:P31 wd:Q515 }"
        query_template = "select distinct ?sbj where { ?sbj wdt:P1376 <obj_1> . ?sbj wdt:P31 <obj_2> }"
        expected_base_template ="select distinct ?sbj where { ?sbj <prop> <obj> . ?sbj wdt:P31 <obj> }"
        self.aux_test_base_template(
            query_string=query_string,
            expected_template=expected_base_template
        )
        self.aux_test_empty_query(
            query_string=query_string,
            expected_template=query_template,
            ignore_type=True
        )
        self.aux_test_base_template(
            query_string=query_template,
            expected_template=expected_base_template
        )


class TestWikidataQueryFixer(unittest.TestCase):
    def test_lcquad2_query_fix(self):
        query = "select ?ent where { ?ent wdt:P31 wd:Q19723451 . ?ent wdt:P4140 ?obj } ?ent wdt:P176 wd:Q16538568 ORDER BY DESC(?obj)LIMIT 5"
        expected_query = "select ?ent where { ?ent wdt:P31 wd:Q19723451 . ?ent wdt:P4140 ?obj . ?ent wdt:P176 wd:Q16538568 } ORDER BY DESC(?obj)LIMIT 5"
        fixed_query = WikidataQueryFixer.lcquad2_query_fix(query)
        self.assertEqual(fixed_query, expected_query)

    def test_change_x_per_obj(self):
        query = "SELECT ?answer WHERE { wd:Q146368 wdt:P4600 ?obj . ?obj wdt:P4952 ?answer}"
        expected_query = "SELECT ?answer WHERE { wd:Q146368 wdt:P4600 ?obj . ?obj wdt:P4952 ?answer}"
        fixed_query = WikidataQueryFixer.change_x_per_obj(query)
        self.assertEqual(fixed_query, expected_query)

    def test_change_sub_per_sbj(self):
        query = "SELECT (COUNT(?sub) AS ?value ) { ?sub wdt:P1196 wd:Q178561 }"
        expected_query = "SELECT (COUNT(?sbj) AS ?value ) { ?sbj wdt:P1196 wd:Q178561 }"
        fixed_query = WikidataQueryFixer.change_sub_per_sbj(query)
        self.assertEqual(fixed_query, expected_query)

    def test_add_where_after_count(self):
        query = "SELECT (COUNT(?obj) AS ?value ) { wd:Q6475 wdt:P1071 ?obj }"
        expected_query = "SELECT (COUNT(?obj) AS ?value ) where { wd:Q6475 wdt:P1071 ?obj }"
        fixed_query = WikidataQueryFixer.add_where_after_count(query)
        self.assertEqual(fixed_query, expected_query)

    def test_remove_t_in_numbers(self):
        "48272"
        query = "ASK WHERE { wd:Q30 wdt:P2997 ?obj filter(?obj = t1410874016) }"
        expected_query = "ASK WHERE { wd:Q30 wdt:P2997 ?obj filter(?obj = 1410874016) }"
        fixed_query = WikidataQueryFixer.remove_t_in_numbers(query)
        self.assertEqual(fixed_query, expected_query)


if __name__ == '__main__':
    unittest.main()
