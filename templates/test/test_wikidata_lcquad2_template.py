import unittest

from templates.wikidata_lcquad2_template import WikidataLcQuad2Template

################################### TEMPLATE TEST CASES ################################################################


class TestWkidataLcQuad2Template(unittest.TestCase):

    def aux_testTemplate(self, temp_string, nnqt, query, expected_query_template, expected_label_entity, expected_slot):
        template=WikidataLcQuad2Template(query, temp_string)
        self.assertEqual(expected_query_template, template.replace_entities(query), "replace: " + str(template))
        self.assertListEqual(expected_label_entity, template.get_label_entity_list(nnqt, query), "label_entity: " + str(template))
        self.assertListEqual(expected_slot, template.get_slot_list(nnqt, query), "slot: " + str(template))

    def testSelectSubjectInstanceOfType(self):
        self.aux_testTemplate(
            temp_string="<?S P O ; ?S InstanceOf Type>",
            nnqt="What is the {city} for {capital of} of {Meghalaya}",
            query=" select distinct ?sbj where { ?sbj wdt:P1376 wd:Q1195 . ?sbj wdt:P31 wd:Q515 } ",
            expected_query_template="select distinct ?sbj where { ?sbj wdt:P1376 <obj_1> . ?sbj wdt:P31 <obj_2> }",
            expected_label_entity=[
                {
                    "label": "city",
                    "entity": "wd:Q515"
                },
                {
                    "label": "Meghalaya",
                    "entity": "wd:Q1195"
                }
            ],
            expected_slot=[
                {
                    "label": "Meghalaya",
                    "slot": "<obj_1>"

                },
                {
                    "label": "city",
                    "slot": "<obj_2>"
                },
            ]
        )

    def testSelectSubjectInstanceOfTypeContainsWord(self):
        self.aux_testTemplate(
            temp_string="<?S P O ; ?S instanceOf Type ; contains word >",
            nnqt="Give me {human} that contains the word {vitellius} in their name",
            query="SELECT DISTINCT ?sbj ?sbj_label WHERE { ?sbj wdt:P31 wd:Q5 . ?sbj rdfs:label ?sbj_label . FILTER(CONTAINS(lcase(?sbj_label), 'vitellius')) . FILTER (lang(?sbj_label)='en') } LIMIT 25 ",
            expected_query_template="SELECT DISTINCT ?sbj ?sbj_label WHERE { ?sbj wdt:P31 <obj_1> . ?sbj rdfs:label ?sbj_label . FILTER(CONTAINS(lcase(?sbj_label), <str_value>)) . FILTER (lang(?sbj_label)='en') } LIMIT 25",
            expected_label_entity=[
                {
                    "label": "human",
                    "entity": "wd:Q5"
                }
            ],
            expected_slot=[
                {
                    "label": "human",
                    "slot": "<obj_1>"
                },
                {
                    "label": "vitellius",
                    "slot": "<str_value>"
                }
            ]
        )

    def testSelectSubjectInstanceOfTypeStartsWith(self):
        self.aux_testTemplate(
            temp_string="<?S P O ; ?S instanceOf Type ; starts with character >",
            nnqt="Give me {city} that starts with {'w'}",
            query="SELECT DISTINCT ?sbj ?sbj_label WHERE { ?sbj wdt:P31 wd:Q515 . ?sbj rdfs:label ?sbj_label . FILTER(STRSTARTS(lcase(?sbj_label), 'w')) . FILTER (lang(?sbj_label)='en') } LIMIT 25 ",
            expected_query_template="SELECT DISTINCT ?sbj ?sbj_label WHERE { ?sbj wdt:P31 <obj_1> . ?sbj rdfs:label ?sbj_label . FILTER(STRSTARTS(lcase(?sbj_label), <str_value>)) . FILTER (lang(?sbj_label)='en') } LIMIT 25",
            expected_label_entity=[
                {
                    "label": "city",
                    "entity": "wd:Q515"
                }
            ],
            expected_slot=[
                {
                    "label": "city",
                    "slot": "<obj_1>"
                },
                {
                    "label": "w",
                    "slot": "<str_value>"
                }
            ]
        )

    def testSelectObjectInstanceOfType(self):
        self.aux_testTemplate(
            temp_string="<S P ?O ; ?O instanceOf Type>",
            nnqt="What is the {city/town} for {twinned administrative body} of {Hamburg}",
            query="select distinct ?obj where { wd:Q1055 wdt:P710 ?obj . ?obj wdt:P31 wd:Q7930989 }",
            expected_query_template="select distinct ?obj where { <sbj_1> wdt:P710 ?obj . ?obj wdt:P31 <obj_2> }",
            expected_label_entity=[
                {
                    "label": "city/town",
                    "entity": "wd:Q7930989"
                },
                {
                    "label": "Hamburg",
                    "entity": "wd:Q1055"
                }
            ],
            expected_slot=[
                {
                    "label": "Hamburg",
                    "slot": "<sbj_1>"
                },
                {
                    "label": "city/town",
                    "slot": "<obj_2>"
                },
            ]
        )

    def testAskOneFact(self):
        self.aux_testTemplate(
            temp_string="Ask (ent-pred-obj)",
            nnqt="Did {Rihanna} {record label} {Motown}?",
            query="ASK WHERE { wd:Q36844 wdt:P264 wd:Q43327 }",
            expected_query_template="ASK WHERE { <sbj_1> wdt:P264 <obj_1> }",
            expected_label_entity=[
                {
                    "label": "Rihanna",
                    "entity": "wd:Q36844"
                },
                {
                    "label": "Motown",
                    "entity": "wd:Q43327"
                }
            ],
            expected_slot=[
                {
                    "label": "Rihanna",
                    "slot": "<sbj_1>"
                },
                {
                    "label": "Motown",
                    "slot": "<obj_1>"
                }
            ]
        )

    def testAskOneFactWithFilter(self):
        self.aux_testTemplate(
            temp_string="ASK ?sbj ?pred ?obj filter ?obj = num",
            nnqt="Does the {family relationship degree} of the {paternal grandmother} {equals} {2}",
            query="ASK WHERE { wd:Q20776714 wdt:P4500 ?obj filter(?obj=2) } ",
            expected_query_template="ASK WHERE { <sbj_1> wdt:P4500 ?obj filter(?obj=<num>) }",
            expected_label_entity=[
                {
                    "label": "paternal grandmother",
                    "entity": "wd:Q20776714"
                }
            ],
            expected_slot=[
                {
                    "label": "paternal grandmother",
                    "slot": "<sbj_1>"
                },
                {
                    "label": "2",
                    "slot": "<num>"
                }
            ]
        )
        self.aux_testTemplate(
            temp_string="ASK ?sbj ?pred ?obj filter ?obj = num",
            nnqt="Does the {heat capacity} of the {water} {equals} {75.375}",
            query="ASK WHERE { wd:Q283 wdt:P2056 ?obj filter(?obj=75.375) } ",
            expected_query_template="ASK WHERE { <sbj_1> wdt:P2056 ?obj filter(?obj=<num>) }",
            expected_label_entity=[
                {
                    "label": "water",
                    "entity": "wd:Q283"
                }
            ],
            expected_slot=[
                {
                    "label": "water",
                    "slot": "<sbj_1>"
                },
                {
                    "label": "75.375",
                    "slot": "<num>"
                }
            ]
        )

    def testAskTwoFacts(self):
        self.aux_testTemplate(
            temp_string="Ask (ent-pred-obj1 . ent-pred-obj2)",
            nnqt="Did {Beijing} {twinned administrative body} {Nur-Sultan} and {Salo} ?",
            query="ASK WHERE { wd:Q956 wdt:P190 wd:Q1520 . wd:Q956 wdt:P190 wd:Q210987 }",
            expected_query_template="ASK WHERE { <sbj_1> wdt:P190 <obj_1> . <sbj_1> wdt:P190 <obj_2> }",
            expected_label_entity=[
                {
                    "label": "Beijing",
                    "entity": "wd:Q956"
                },
                {
                    "label": "Nur-Sultan",
                    "entity": "wd:Q1520"
                },
                {
                    "label": "Salo",
                    "entity": "wd:Q210987"
                }
            ],
            expected_slot=[
                {
                    "label": "Beijing",
                    "slot": "<sbj_1>"
                },
                {
                    "label": "Nur-Sultan",
                    "slot": "<obj_1>"
                },
                {
                    "label": "Salo",
                    "slot": "<obj_2>"
                }
            ]
        )

    def testSelectOneFactSubject(self):
        self.aux_testTemplate(
            temp_string="E REF ?F",
            nnqt="What is <SANU member ID> of <Roman Jakobson> ?",
            query="select distinct ?answer where { wd:Q156201 wdt:P3475 ?answer}",
            expected_query_template="select distinct ?answer where { <sbj_1> wdt:P3475 ?answer}",
            expected_label_entity=[
                {
                    "label": "Roman Jakobson",
                    "entity": "wd:Q156201"
                }
            ],
            expected_slot=[
                {
                    "label": "Roman Jakobson",
                    "slot": "<sbj_1>"
                }
            ]
        )

    def testSelectOneFactObject(self):
        self.aux_testTemplate(
            temp_string="?D RDE E",
            nnqt="What is <this zoological name is coordinate with> of <Papilionidae> ?",
            query="select distinct ?answer where { ?answer wdt:P2743 wd:Q59905}",
            expected_query_template="select distinct ?answer where { ?answer wdt:P2743 <obj_1>}",
            expected_label_entity=[
                {
                    "label": "Papilionidae",
                    "entity": "wd:Q59905"
                }
            ],
            expected_slot=[
                {
                    "label": "Papilionidae",
                    "slot": "<obj_1>"
                }
            ]
        )

    def testSelectTwoAnswers(self):
        self.aux_testTemplate(
            temp_string="select where (ent-pred-obj1 . ent-pred-obj2)",
            nnqt="What is the {child} and the {place of birth} of {Ashton_Kutcher} ?",
            query="SELECT ?ans_1 ?ans_2 WHERE { wd:Q164782 wdt:P40 ?ans_1 . wd:Q164782 wdt:P19 ?ans_2 }",
            expected_query_template="SELECT ?ans_1 ?ans_2 WHERE { <sbj_1> wdt:P40 ?ans_1 . <sbj_1> wdt:P19 ?ans_2 }",
            expected_label_entity=[
                {
                    "label": "Ashton_Kutcher",
                    "entity": "wd:Q164782"
                }
            ],
            expected_slot=[
                {
                    "label": "Ashton_Kutcher",
                    "slot": "<sbj_1>"
                }
            ]
        )

    def testSelectTwoFactsSubjectObject(self):
        self.aux_testTemplate(
            temp_string="E REF ?F . ?F RFG G",
            nnqt="What is {capital town} of {Kingdom of Wessex}, that has {notable event} is {7 July 2005 London bombings} ?",
            query="SELECT ?answer WHERE { wd:Q105313 wdt:P36 ?answer . ?answer wdt:P793 wd:Q10818}",
            expected_query_template="SELECT ?answer WHERE { <sbj_1> wdt:P36 ?answer . ?answer wdt:P793 <obj_2>}",
            expected_label_entity=[
                {
                    "label": "Kingdom of Wessex",
                    "entity": "wd:Q105313"
                },
                {
                    "label": "7 July 2005 London bombings",
                    "entity": "wd:Q10818"
                }
            ],
            expected_slot=[
                {
                    "label": "Kingdom of Wessex",
                    "slot": "<sbj_1>"
                },
                {
                    "label": "7 July 2005 London bombings",
                    "slot": "<obj_2>"
                }
            ]
        )

    def testSelectTwoFactsRightSubject(self):
        self.aux_testTemplate(
            temp_string="E REF xF . xF RFG ?G",
            nnqt="What is {safety classification and labelling} of {polymer of} of {polyvinyl chloride} ?",
            query="SELECT ?answer WHERE { wd:Q146368 wdt:P4600 ?X . ?X wdt:P4952 ?answer}",
            expected_query_template="SELECT ?answer WHERE { <sbj_1> wdt:P4600 ?obj . ?obj wdt:P4952 ?answer}",
            expected_label_entity=[
                {
                    "label": "polyvinyl chloride",
                    "entity": "wd:Q146368"
                }
            ],
            expected_slot=[
                {
                    "label": "polyvinyl chloride",
                    "slot": "<sbj_1>"
                }
            ]
        )

    def testSelectTwoFactsLeftSubject(self):
        self.aux_testTemplate(
            temp_string="C RCD xD . xD RDE ?E",
            nnqt="What is {has influence} of {brother or sister} of {Paul Wittgenstein} ?",
            query="SELECT ?answer WHERE { wd:Q170348 wdt:P3373 ?X . ?X wdt:P737 ?answer}",
            expected_query_template="SELECT ?answer WHERE { <sbj_1> wdt:P3373 ?obj . ?obj wdt:P737 ?answer}",
            expected_label_entity=[
                {
                    "label": "Paul Wittgenstein",
                    "entity": "wd:Q170348"
                }
            ],
            expected_slot=[
                {
                    "label": "Paul Wittgenstein",
                    "slot": "<sbj_1>"
                }
            ]
        )

    def testCountOneFactSubject(self):
        self.aux_testTemplate(
            temp_string="Count ent (ent-pred-obj)",
            nnqt="How many {manner of death} are to/by {battle} ?",
            query="SELECT (COUNT(?sub) AS ?value ) { ?sub wdt:P1196 wd:Q178561 }",
            expected_query_template="SELECT (COUNT(?sbj) AS ?value ) where { ?sbj wdt:P1196 <obj_1> }",
            expected_label_entity=[
                {
                    "label": "battle",
                    "entity": "wd:Q178561"
                }
            ],
            expected_slot=[
                {
                    "label": "battle",
                    "slot": "<obj_1>"
                }
            ]
        )

    def testCountOneFactObject(self):
        self.aux_testTemplate(
            temp_string="Count Obj (ent-pred-obj)",
            nnqt="How many {location of final assembly} are for {Airbus A320} ?",
            query="SELECT (COUNT(?obj) AS ?value ) { wd:Q6475 wdt:P1071 ?obj }",
            expected_query_template="SELECT (COUNT(?obj) AS ?value ) where { <sbj_1> wdt:P1071 ?obj }",
            expected_label_entity=[
                {
                    "label": "Airbus A320",
                    "entity": "wd:Q6475"
                }
            ],
            expected_slot=[
                {
                    "label": "Airbus A320",
                    "slot": "<sbj_1>"
                }
            ]
        )

    def testSelectOneQualifierValueUsingOneStatementProperty(self):
        self.aux_testTemplate(
            temp_string="(E pred ?Obj ) prop value",
            nnqt="what is the {criterion used} for {Eros} has {mother} as {Nyx} ?",
            query="SELECT ?value WHERE { wd:Q121973 p:P25 ?s . ?s ps:P25 wd:Q131203 . ?s pq:P1013 ?value}",
            expected_query_template="SELECT ?value WHERE { <sbj_1> p:P25 ?s . ?s ps:P25 <obj_2> . ?s pq:P1013 ?value}",
            expected_label_entity=[
                {
                    "label": "Eros",
                    "entity": "wd:Q121973"
                },
                {
                    "label": "Nyx",
                    "entity": "wd:Q131203"
                }
            ],
            expected_slot=[
                {
                    "label": "Eros",
                    "slot": "<sbj_1>"
                },
                {
                    "label": "Nyx",
                    "slot": "<obj_2>"
                }
            ]
        )
        self.aux_testTemplate(
            temp_string="(E pred ?Obj ) prop value",
            nnqt="what is the {has quality} for {Heidelberg University} has {IPv4 routing prefix} as {129.206.0.0/16} ?",
            query="SELECT ?value WHERE { wd:Q151510 p:P3761 ?s . ?s ps:P3761 ?x filter(contains(?x,'129.206.0.0/16')) . ?s pq:P1552 ?value}",
            expected_query_template="SELECT ?value WHERE { <sbj_1> p:P3761 ?s . ?s ps:P3761 ?x filter(contains(?x,<str_value>)) . ?s pq:P1552 ?value}",
            expected_label_entity=[
                {
                    "label": "Heidelberg University",
                    "entity": "wd:Q151510"
                }
            ],
            expected_slot=[
                {
                    "label": "Heidelberg University",
                    "slot": "<sbj_1>"
                },
                {
                    "label": "129.206.0.0/16",
                    "slot": "<str_value>"
                }
            ]
        )

    def testSelectObjectUsingOneStatementProperty(self):
        self.aux_testTemplate(
            temp_string="(E pred F) prop ?value",
            nnqt="What is {position held} of {Mieszko I} that is {replaced by} is {Boles\u0142aw I Chrobry} ?",
            query="SELECT ?obj WHERE { wd:Q53435 p:P39 ?s . ?s ps:P39 ?obj . ?s pq:P1366 wd:Q53436 }",
            expected_query_template="SELECT ?obj WHERE { <sbj_1> p:P39 ?s . ?s ps:P39 ?obj . ?s pq:P1366 <obj_3> }",
            expected_label_entity=[
                {
                    "label": "Mieszko I",
                    "entity": "wd:Q53435"
                },
                {
                    "label": "Boles\u0142aw I Chrobry",
                    "entity": "wd:Q53436"
                }
            ],
            expected_slot=[
                {
                    "label": "Mieszko I",
                    "slot": "<sbj_1>"
                },
                {
                    "label": "Boles\u0142aw I Chrobry",
                    "slot": "<obj_3>"
                }
            ]
        )
        self.aux_testTemplate(
            temp_string="(E pred F) prop ?value",
            nnqt="What is {spouse} of {Nero} that is {end time} is {68-6-9} ?",
            query="SELECT ?obj WHERE { wd:Q1413 p:P26 ?s . ?s ps:P26 ?obj . ?s pq:P582 ?x filter(contains(?x,'68-6-9')) }",
            expected_query_template="SELECT ?obj WHERE { <sbj_1> p:P26 ?s . ?s ps:P26 ?obj . ?s pq:P582 ?x filter(contains(?x,<str_value>)) }",
            expected_label_entity=[
                {
                    "label": "Nero",
                    "entity": "wd:Q1413"
                }
            ],
            expected_slot=[
                {
                    "label": "Nero",
                    "slot": "<sbj_1>"
                },
                {
                    "label": "68-6-9",
                    "slot": "<str_value>"
                }
            ]
        )

    def testRankInstanceOfTypeOneFact(self):
        self.aux_testTemplate(
            temp_string="?E is_a Type, ?E pred Obj  value. MAX/MIN (value)",
            nnqt="What is the {independent city} with the {MAX(vehicles per capita (1000))} ?",
            query="select ?ent where { ?ent wdt:P31 wd:Q22865 . ?ent wdt:P5167 ?obj } ORDER BY DESC(?obj)LIMIT 5 ",
            expected_query_template="select ?ent where { ?ent wdt:P31 <obj_1> . ?ent wdt:P5167 ?obj } ORDER BY DESC(?obj)LIMIT 5",
            expected_label_entity=[
                {
                    "label": "independent city",
                    "entity": "wd:Q22865"
                }
            ],
            expected_slot=[
                {
                    "label": "independent city",
                    "slot": "<obj_1>"
                }
            ]
        )
        self.aux_testTemplate(
            temp_string="?E is_a Type, ?E pred Obj  value. MAX/MIN (value)",
            nnqt="What is the {weapon model} with the {MIN(rate of fire)} ?",
            query="select ?ent where { ?ent wdt:P31 wd:Q15142894 . ?ent wdt:P3792 ?obj } ORDER BY ASC(?obj)LIMIT 5 ",
            expected_query_template="select ?ent where { ?ent wdt:P31 <obj_1> . ?ent wdt:P3792 ?obj } ORDER BY ASC(?obj)LIMIT 5",
            expected_label_entity=[
                {
                    "label": "weapon model",
                    "entity": "wd:Q15142894"
                }
            ],
            expected_slot=[
                {
                    "label": "weapon model",
                    "slot": "<obj_1>"
                }
            ]
        )

    def testRankMaxInstanceOfTypeTwoFacts(self):
        self.aux_testTemplate(
            temp_string="?E is_a Type. ?E pred Obj. ?E-secondClause value. MAX (value)",
            nnqt="What is the {smartphone model} with the {MAX(energy storage capacity)} whose {manufacturer} is {Microsoft Mobile}  ?",
            query="select ?ent where { ?ent wdt:P31 wd:Q19723451 . ?ent wdt:P4140 ?obj } ?ent wdt:P176 wd:Q16538568 ORDER BY DESC(?obj)LIMIT 5 ",
            expected_query_template="select ?ent where { ?ent wdt:P31 <obj_1> . ?ent wdt:P4140 ?obj . ?ent wdt:P176 <obj_3> } ORDER BY DESC(?obj)LIMIT 5",
            expected_label_entity=[
                {
                    "label": "smartphone model",
                    "entity": "wd:Q19723451"
                },
                {
                    "label": "Microsoft Mobile",
                    "entity": "wd:Q16538568"
                }
            ],
            expected_slot=[
                {
                    "label": "smartphone model",
                    "slot": "<obj_1>"
                },
                {
                    "label": "Microsoft Mobile",
                    "slot": "<obj_3>"
                }
            ]
        )

    def testRankMinInstanceOfTypeTwoFacts(self):
        self.aux_testTemplate(
            temp_string="?E is_a Type. ?E pred Obj. ?E-secondClause value. MIN (value)",
            nnqt="What is the {state of Germany} with the {MIN(vehicles per capita (1000))} whose {contains administrative territorial entity} is {ERROR1}  ?",
            query="select ?ent where { ?ent wdt:P31 wd:Q1221156 . ?ent wdt:P5167 ?obj } ?ent wdt:P150 wd:Q30127558 ORDER BY ASC(?obj)LIMIT 5 ",
            expected_query_template="select ?ent where { ?ent wdt:P31 <obj_1> . ?ent wdt:P5167 ?obj . ?ent wdt:P150 <obj_3> } ORDER BY ASC(?obj)LIMIT 5",
            expected_label_entity=[
                {
                    "label": "state of Germany",
                    "entity": "wd:Q1221156"
                },
                {
                    "label": "ERROR1",
                    "entity": "wd:Q30127558"
                }
            ],
            expected_slot=[
                {
                    "label": "state of Germany",
                    "slot": "<obj_1>"
                },
                {
                    "label": "ERROR1",
                    "slot": "<obj_3>"
                }
            ]
        )

    def testSelectOneQualifierValueAndObjectUsingOneStatementProperty(self):
        self.aux_testTemplate(
            temp_string=3,
            nnqt="What is {award received} of {Konrad Lorenz} and {together with}",
            query="SELECT ?value1 ?obj WHERE { wd:Q78496 p:P166 ?s . ?s ps:P166 ?obj . ?s pq:P1706 ?value1 . }",
            expected_query_template="SELECT ?value1 ?obj WHERE { <sbj_1> p:P166 ?s . ?s ps:P166 ?obj . ?s pq:P1706 ?value1 . }",
            expected_label_entity=[
                {
                    "label": "Konrad Lorenz",
                    "entity": "wd:Q78496"
                }
            ],
            expected_slot=[
                {
                    "label": "Konrad Lorenz",
                    "slot": "<sbj_1>"
                }
            ]
        )

    def testSelectTwoQualifierValuesUsingOneStatementProperty(self):
        self.aux_testTemplate(
            temp_string=2,
            nnqt="What is {point in time} and {together with} of {{Bob Barker} has {award received} as {MTV Movie Award for Best Fight}}",
            query="SELECT ?value1 ?value2 WHERE { wd:Q381178 p:P166 ?s . ?s ps:P166 wd:Q734036 . ?s pq:P585 ?value1 . ?s pq:P1706 ?value2 }",
            expected_query_template="SELECT ?value1 ?value2 WHERE { <sbj_1> p:P166 ?s . ?s ps:P166 <obj_2> . ?s pq:P585 ?value1 . ?s pq:P1706 ?value2 }",
            expected_label_entity=[
                {
                    "label": "Bob Barker",
                    "entity": "wd:Q381178"
                },
                {
                    "label": "MTV Movie Award for Best Fight",
                    "entity": "wd:Q734036"
                }
            ],
            expected_slot=[
                {
                    "label": "Bob Barker",
                    "slot": "<sbj_1>"
                },
                {
                    "label": "MTV Movie Award for Best Fight",
                    "slot": "<obj_2>"
                }
            ]
        )

if __name__ == '__main__':
    unittest.main()