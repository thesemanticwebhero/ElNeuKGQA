from typing import List, Dict, Union

from query_tools import Query
from templates.base_template import Template
from templates.templates_lcquad_2 import TemplateLCQUAD2
from templates.wikidata_template import WikidataTemplate


class WikidataLcQuad2Template(Template):

    def __init__(self, query_string: Union[str, Query], template_string: Union[str, int]):
        if isinstance(query_string, Query):
            self.query_string = str(query_string)
        self.lcquad2_template = TemplateLCQUAD2.create_template(template_string)
        self.wikidata_template = WikidataTemplate(query_string)

    def get_lcquad2_template_name(self):
        return self.lcquad2_template.get_intent()

    def replace_entities(self, query: str) -> str:
        return self.wikidata_template.replace_entities(query)

    def get_label_entity_list(self, question: str, query: str) -> List[Dict]:
        return self.lcquad2_template.get_label_entity_list(question, query)

    def get_slot_list(self, nnqt: str, query_string: str) -> List[Dict]:
        slots = self.wikidata_template.get_slots()
        entities = self.get_label_entity_list(nnqt, query_string)
        slot_list = list()
        for entity, slot in slots.items():
            if slot == '<num>' or slot == '<str_value>':
                slot_list.append(dict(slot=slot, label=entity))
            else:
                for entity_dict in entities:
                    if entity_dict['entity'] == entity:
                        slot_list.append(dict(slot=slot, label=entity_dict['label']))
        return slot_list

    def __str__(self):
        return str(self.lcquad2_template)
