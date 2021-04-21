import re
from collections import deque
from enum import Enum
from typing import Iterable, Tuple, Dict, List, Optional

from dataset_tools import Normalizer


class BaseQueryGenerationSlotFillingHelperMethodNotImplemented(Exception):
    pass


class BaseQueryGenerationSlotFillingHelper:

    def fill_template(self, query_template: str, slots: Dict, entities: List[Dict]) -> Tuple[str, List[Dict]]:
        raise BaseQueryGenerationSlotFillingHelperMethodNotImplemented


class BasicQueryGenerationSlotFillingHelper(BaseQueryGenerationSlotFillingHelper):

    def fill_template(self, query_template: str, slots: Dict, entities: List[Dict]) -> Tuple[str, List[Dict]]:
        sparql_query = query_template
        slot_entity_map = list()
        for label, placeholder in slots.items():
            if placeholder == '<num>':
                sparql_query = re.sub(placeholder, '.'.join(label.split(' ')), sparql_query)
                slot_entity_map.append(dict(slot=placeholder, entity='.'.join(label.split(' '))))
            elif placeholder in ['<label>', '<letter>', '<str_value>']:
                sparql_query = re.sub(placeholder, f"'{label}'", sparql_query)
                slot_entity_map.append(dict(slot=placeholder, entity=f"'{label}'"))
            else:
                for entity_case in entities:
                    entity_label = entity_case['label'].lower()
                    if label in entity_label or entity_label in label:
                        sparql_query = re.sub(placeholder, entity_case['url'], sparql_query)
                        slot_entity_map.append(dict(slot=placeholder, entity=entity_case['url']))
                        break
        return sparql_query, slot_entity_map


class StandardQueryGenerationSlotFillingHelper(BaseQueryGenerationSlotFillingHelper):

    def fill_template(self, query_template: str, slots: Dict, entities: List[Dict]) -> Tuple[str, List[Dict]]:
        sparql_query = query_template
        slot_entity_map = list()
        used_slots = set()
        used_entities = set()
        for label, placeholder in slots.items():
            if placeholder in used_slots or placeholder not in sparql_query:
                continue
            if placeholder == '<num>':
                used_slots.add(placeholder)
                sparql_query = re.sub(placeholder, '.'.join(label.split(' ')), sparql_query)
                slot_entity_map.append(dict(slot=placeholder, entity='.'.join(label.split(' '))))
            elif placeholder == '<str_value>':
                used_slots.add(placeholder)
                sparql_query = re.sub(placeholder, f"'{label}'", sparql_query)
                slot_entity_map.append(dict(slot=placeholder, entity=f"'{label}'"))
            else:
                entity_url = None
                for entity_case in entities:
                    entity_label = Normalizer.normalize_question(entity_case['label'])
                    if label in entity_label or entity_label in label:
                        entity_url = entity_case['url']
                        break
                if entity_url:
                    used_slots.add(placeholder)
                    used_entities.add(entity_url)
                    sparql_query = re.sub(placeholder, entity_url, sparql_query)
                    slot_entity_map.append(dict(slot=placeholder, entity=entity_url))
        return sparql_query, slot_entity_map


class ForceQueryGenerationSlotFillingHelper:

    @staticmethod
    def digit(case: str) -> int:
        return int(re.search('(\d+)', case).group(1) if re.search('(\d+)', case) else 100)

    @staticmethod
    def triple_position(case: str):
        return re.search('(sbj|obj|type)', case).group(1) if re.search('(sbj|obj|type)', case) else 'other'

    def sorted_remaining_slots(self, slots: Iterable[str]) -> Iterable[str]:
        slots_opts = ['sbj', 'obj', 'type', 'other']
        return sorted(slots, key=lambda case: (self.digit(case[1]), slots_opts.index(self.triple_position(case[1]))))

    @staticmethod
    def search_valid_entity(label:str, remaining_entities: deque, flexible: bool = False) -> Optional[str]:
        entity_url = None
        remaining_entities.append('<END>')
        # look into remaining entities
        while remaining_entities:
            entity_case = remaining_entities.popleft()
            if entity_case == '<END>':
                break
            entity_label = Normalizer.normalize_question(entity_case['label'])
            # exact match or "fuzzy" match
            if (not flexible and entity_label == label) or \
                    (flexible and (label in entity_label or entity_label in label)):
                entity_url = entity_case['url']
                remaining_entities.remove('<END>')
                break
            remaining_entities.append(entity_case)
        return entity_url

    def fill_template(self, query_template: str, slots: Dict, entities: List[Dict]) -> Tuple[str, List[Dict]]:
        sparql_query = query_template
        slot_entity_map = list()
        used_slots = set()
        remaining_entities = deque(entities)
        slots_to_be_filled = deque(re.findall('<[\w_\d]+?>', sparql_query))
        slots_to_be_filled.append('<END>')
        while slots_to_be_filled:
            slot = slots_to_be_filled.popleft()
            # remove duplicates
            if slot in used_slots:
                continue
            # if all slots have been checked
            if slot == '<END>':
                break
            success = False
            for label, placeholder in slots.items():
                if placeholder != slot:
                    continue
                if placeholder == '<num>':
                    num_label = '.'.join(label.split(' '))
                    sparql_query = re.sub(placeholder, num_label, sparql_query)
                    used_slots.add(placeholder)
                    slot_entity_map.append(dict(slot=placeholder, entity=num_label))
                    success = True
                elif placeholder == '<str_value>':
                    str_label = f"'{label}'"
                    sparql_query = re.sub(placeholder, str_label, sparql_query)
                    used_slots.add(placeholder)
                    slot_entity_map.append(dict(slot=placeholder, entity=str_label))
                    success = True
                else:
                    entity_url = self.search_valid_entity(label, remaining_entities, flexible=False)
                    sparql_query = re.sub(placeholder, entity_url, sparql_query) if entity_url else sparql_query
                    if entity_url:
                        success = True
                        used_slots.add(placeholder)
                        slot_entity_map.append(dict(slot=placeholder, entity=entity_url))
            if not success:
                slots_to_be_filled.append(slot)
        # if there still are some slots to be filled
        remaining_slots_items = filter(lambda case: case[1] not in used_slots, slots.items())
        remaining_slots_items = deque(self.sorted_remaining_slots(remaining_slots_items))
        while slots_to_be_filled:
            slot = slots_to_be_filled.popleft()
            success = False
            if not remaining_entities:
                break
            # Just fill whatever is left
            if not remaining_slots_items:
                entity_url = remaining_entities.popleft()['url']
                sparql_query = re.sub(slot, entity_url, sparql_query)
                slot_entity_map.append(dict(slot=slot, entity=entity_url))
                continue
            remaining_slots_items.append('<END>')
            # look into remaining slots_items
            while remaining_slots_items:
                slot_item = remaining_slots_items.popleft()
                if slot_item == '<END>':
                    break
                label, placeholder = slot_item
                # not fuzzy matched
                if not (self.digit(slot) == self.digit(placeholder) or self.triple_position(
                        slot) == self.triple_position(placeholder)):
                    remaining_slots_items.append(slot_item)
                    continue
                entity_url = self.search_valid_entity(label, remaining_entities, flexible=True)
                if entity_url:
                    success = True
                    sparql_query = re.sub(slot, entity_url, sparql_query)
                    remaining_slots_items.remove('<END>')
                    slot_entity_map.append(dict(slot=slot, entity=entity_url))
                    break
            if not success:
                entity_url = remaining_entities.popleft()['url']
                sparql_query = re.sub(slot, entity_url, sparql_query)
                slot_entity_map.append(dict(slot=slot, entity=entity_url))
        return sparql_query, slot_entity_map


class SlotFillingMethodEnum(Enum):
    basic = BasicQueryGenerationSlotFillingHelper
    standard = StandardQueryGenerationSlotFillingHelper
    force = ForceQueryGenerationSlotFillingHelper
