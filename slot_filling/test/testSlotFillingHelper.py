import unittest
from typing import Dict, List

from slot_filling.qa_slot_filling_helper import ForceQueryGenerationSlotFillingHelper


class TestSlotFillingHelper(unittest.TestCase):
    def auxTestForceFill(self, query_template: str, slots: Dict, entities: List[Dict], expected_answer: str,
                         expected_slot_entity_map: List[Dict],
                         do_assert: bool = True):
        system_answer, system_slot_entity_map = ForceQueryGenerationSlotFillingHelper().fill_template(query_template, slots, entities)
        if do_assert:
            self.assertEqual(expected_answer, system_answer)
            self.assertListEqual(expected_slot_entity_map, system_slot_entity_map)
            # self.assertEqual(set(tuple([case['slot'], case['entity']]) for case in expected_slot_entity_map), set(tuple([case['slot'], case['entity']]) for case in system_slot_entity_map))
        else:
            print("EXPECTED: ", expected_answer)
            print("SYSTEM:   ", system_answer)

    def testForceFillSlotCorrectlyLabeled(self):
        # Labels correctly assigned
        self.auxTestForceFill(
            query_template="ask where { <sbj_1> wdt:P103 <obj_1> }",
            slots={
                "john f kennedy": "<sbj_1>",
                "old english": "<obj_1>"
            },
            entities=[
                {
                    "ini": 4,
                    "fin": 19,
                    "label": "John F. Kennedy",
                    "url": "wd:Q9696",
                    "score_list": [
                        {
                            "value": 0.9665,
                            "field_name": "disambiguationScore"
                        }
                    ]
                },
                {
                    "ini": 38,
                    "fin": 49,
                    "label": "Old English",
                    "url": "wd:Q42365",
                    "score_list": [
                        {
                            "value": 0.42504,
                            "field_name": "disambiguationScore"
                        }
                    ]
                }
            ],
            expected_answer="ask where { wd:Q9696 wdt:P103 wd:Q42365 }",
            expected_slot_entity_map=[
                dict(slot='<sbj_1>', entity='wd:Q9696'),
                dict(slot='<obj_1>', entity='wd:Q42365'),
            ],
        )

    def testForceFillSlotMissing(self):
        # One slot missing: <obj_1>
        self.auxTestForceFill(
            query_template="ask where { <sbj_1> wdt:P27 <obj_1> }",
            slots = {"lil wayne": "<sbj_1>"},
            entities = [
                {
                    "ini": 3,
                    "fin": 12,
                    "label": "Lil Wayne",
                    "url": "wd:Q15615",
                    "score_list": [{"value": 25.65301366603667, "field_name": "log_likelihood"}]
                },
                {
                    "ini": 15,
                    "fin": 17,
                    "label": "US",
                    "url": "wd:Q30",
                    "score_list": [{"value": 1.0, "field_name": "disambiguationScore"}]
                }
            ],
            expected_answer = "ask where { wd:Q15615 wdt:P27 wd:Q30 }",
            expected_slot_entity_map=[
                dict(slot='<sbj_1>', entity='wd:Q15615'),
                dict(slot='<obj_1>', entity='wd:Q30'),
            ],
        )

    def testForceFillSlotIncorrectlyTagged(self):
        # One slot incorrectly tagged: <obj_2> instead of <obj_1>
        self.auxTestForceFill(
            query_template="ask where { <sbj_1> wdt:P26 <obj_1> }",
            slots= {
                    "stephen curry": "<sbj_1>",
                    "rachael ray": "<obj_2>"
            },
            entities= [
                {
                    "ini": 22,
                    "fin": 33,
                    "label": "Rachael Ray",
                    "url": "wd:Q257943",
                    "score_list": [
                        {
                            "value": 24.912549928495714,
                            "field_name": "log_likelihood"
                        }
                    ]
                },
                {
                    "ini": 4,
                    "fin": 17,
                    "label": "Stephen Curry",
                    "url": "wd:Q352159",
                    "score_list": [
                        {
                            "value": 0.5002393126487732,
                            "field_name": "rho"
                        }
                    ]
                }
            ],
            expected_answer="ask where { wd:Q352159 wdt:P26 wd:Q257943 }",
            expected_slot_entity_map=[
                dict(slot='<sbj_1>', entity='wd:Q352159'),
                dict(slot='<obj_1>', entity='wd:Q257943'),
            ],
        )

    def testForceFillOneLabelContainedInOtherOne(self):
        # Label "fibonacci" is a substring of the label "fibonacci sequence"
        self.auxTestForceFill(
            query_template="ask where { <sbj_1> wdt:P138 <obj_1> }",
            slots={
                "fibonacci sequence": "<sbj_1>",
                "fibonacci": "<obj_1>"
            },
            entities=[
                {
                    "ini": 39,
                    "fin": 48,
                    "label": "Fibonacci",
                    "url": "wd:Q8763",
                    "score_list": [
                        {
                            "value": 14.069714998388692,
                            "field_name": "log_likelihood"
                        }
                    ]
                },
                {
                    "ini": 4,
                    "fin": 22,
                    "label": "Fibonacci Sequence",
                    "url": "wd:Q47577",
                    "score_list": [
                        {
                            "value": 0.4509202539920807,
                            "field_name": "rho"
                        }
                    ]
                }
            ],
            expected_answer="ask where { wd:Q47577 wdt:P138 wd:Q8763 }",
            expected_slot_entity_map=[
                dict(slot='<sbj_1>', entity='wd:Q47577'),
                dict(slot='<obj_1>', entity='wd:Q8763'),
            ],
        )

    def testForceFillNotExactMatchedLabels(self):
        # Label "nebula award for best script" assigned to "Nebula Award"
        self.auxTestForceFill(
            query_template="ask where { <sbj_1> wdt:P1411 <obj_1> }",
            slots={
                "ron howard": "<sbj_1>",
                "nebula award for best script": "<obj_1>"
            },
            entities=[
                {
                    "ini": 4,
                    "fin": 14,
                    "label": "Ron Howard",
                    "url": "wd:Q103646",
                    "score_list": [
                        {
                            "value": 1.0,
                            "field_name": "disambiguationScore"
                        }
                    ]
                },
                {
                    "ini": 45,
                    "fin": 57,
                    "label": "Nebula Award",
                    "url": "wd:Q194285",
                    "score_list": [
                        {
                            "value": 0.561386227607727,
                            "field_name": "rho"
                        }
                    ]
                }
            ],
            expected_answer="ask where { wd:Q103646 wdt:P1411 wd:Q194285 }",
            expected_slot_entity_map=[
                dict(slot='<sbj_1>', entity='wd:Q103646'),
                dict(slot='<obj_1>', entity='wd:Q194285'),
            ],
        )