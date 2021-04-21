import re

from typing import List, Dict, Tuple, Union

from query_tools import WikidataQuery, Query
from templates.base_template import Template


class QueryTriple:
    def __init__(self, sbj: str, pred: str, obj: str):
        self.subject = sbj
        self.predicate = pred
        self.object = obj

    @property
    def sbj(self) -> str:
        return self.subject

    @property
    def pred(self) -> str:
        return self.predicate

    @property
    def obj(self) -> str:
        return self.object

    @classmethod
    def from_match_obj(cls, match_object):
        return cls(match_object.group('sbj'), match_object.group('prop'), match_object.group('obj'))


class WikidataQueryFixer:

    @staticmethod
    def lcquad2_template_fix(query_string: str) -> str:
        FIX_PATTERN = re.compile(r"""
                    }
                    \s+
                    (?P<sbj>\?\w+)
                    \s+
                    (?P<prop>(\w+:P\d+)|(<[\w\d_]+?>))
                    \s+
                    (?P<obj><[\w\d_]+?>)
                    """, re.X)
        query_string = FIX_PATTERN.sub(". \g<sbj> \g<prop> \g<obj> }", query_string)
        return query_string

    @staticmethod
    def lcquad2_query_fix(query_string: str) -> str:
        FIX_PATTERN = re.compile(r"""
                        }
                        \s+
                        (?P<sbj>(?:\?\w+)|<[\w\d_]+?>|(?:wd:Q\d+))  # subject
                        \s+
                        (?P<prop>(\w+:P\d+)|(\w+:\w+)|[\^+*/])+ # property (or prop path)
                        \s+
                        (?P<obj>(?:\?\w+)|<[\w\d_]+?>|(?:wd:Q\d+))  # object
                        """, re.X)
        query_string = FIX_PATTERN.sub(". \g<sbj> \g<prop> \g<obj> }", query_string)
        return query_string

    @staticmethod
    def change_x_per_obj(query_string: str):
        return re.sub(r'\?X', '?obj', query_string)

    @staticmethod
    def change_sub_per_sbj(query_string: str):
        return re.sub(r'\?sub', '?sbj', query_string)

    @staticmethod
    def add_where_after_count(query_string: str) -> str:
        if 'where' not in query_string.lower():
            return re.subn(r'{', 'where {', query_string, count=1)[0]
        return query_string

    @staticmethod
    def remove_t_in_numbers(query_string: str) -> str:
        return re.sub(r'([=<>])\s+t(\d)', '\g<1> \g<2>', query_string)


class WikidataQueryPatternHelper:

    @staticmethod
    def get_query_triples_matches():
        return re.compile(r"""
                        (?P<sbj>(?:\?\w+)|<[\w\d_]+?>|(?:wd:Q\d+))  # subject
                        \s+
                        (?P<prop>(\w+:P\d+)|(\w+:\w+)|[\^+*/])+ # property (or prop path)
                        \s+
                        (?P<obj>(?:\?\w+)|<[\w\d_]+?>|(?:wd:Q\d+))  # object
                        """, re.X)

    @staticmethod
    def type_entities(query_string: str) -> List[str]:
        ENTITY_TYPE_PATTERN = re.compile(r"""
        (?P<sbj>(?:\?\w+)|(?:wd:Q\d+))  # subject
        \s+
        (?:(wdt:P31)|(wdt:P279)|(wdt:P273)|[\^+*/])+ # property (P31 or P279 + prop path)
        \s+
        (?P<type>(?:\?\w+)|(?:wd:Q\d+)) # object
        """, re.X)
        return [case.group('type') for case in ENTITY_TYPE_PATTERN.finditer(query_string)]

    @staticmethod
    def str_values_fix(query_string: str) -> Tuple[str, str]:
        STRING_VALUE_PATTERN = re.compile(r"""
                '(.*?)'
                """, re.X)
        str_value = STRING_VALUE_PATTERN.search(query_string).group(1) if STRING_VALUE_PATTERN.search(query_string) else None
        query_string = STRING_VALUE_PATTERN.sub("<str_value>", query_string, count=1)
        return query_string, str_value

    @staticmethod
    def number_fix(query_string: str) -> Tuple[str, str]:
        LIMIT_NUM_PATTERN = re.compile(r"""
                    (?<=LIMIT|limit)                    
                    (?P<limit>\s+\d+)
                    """, re.X)
        if LIMIT_NUM_PATTERN.search(query_string):
            limit = LIMIT_NUM_PATTERN.search(query_string).group(1)
            query_string = LIMIT_NUM_PATTERN.sub("<limit>", query_string)
        else:
            limit = None
        NUMBER_PATTERN = re.compile(r"""
                    (?<=[^_\w])
                    (?P<num>
                    [-t]?
                    (\d+)
                    (\.\d+)?
                    (e[+-]?\d+)?
                    )
                    """, re.X)
        # ((\d+)(?P<dot_or_exp>\.|(e[+-]?))(?(dot_or_exp)\d+)))|(\d+))
        number = NUMBER_PATTERN.search(query_string).group('num') if NUMBER_PATTERN.search(query_string) else None
        query_string = NUMBER_PATTERN.sub("<num>", query_string)
        return query_string if not limit else re.sub('<limit>', limit, query_string), number

    @staticmethod
    def unify_filter_op(query_string: str) -> str:
        FIX_PATTERN = re.compile(r"""
                    (?P<operator>[<=>])(?=\s+?<num>)
                    """, re.X)
        query_string = FIX_PATTERN.sub("[<=>]", query_string)
        return query_string

    @staticmethod
    def unify_asc_desc_op(query_string: str) -> str:
        FIX_PATTERN = re.compile(r"""
                        (?P<operator>ASC|DESC)
                        """, re.X)
        query_string = FIX_PATTERN.sub("[ASC|DESC]", query_string)
        return query_string

    @staticmethod
    def have_non_entities(query_string: str) -> bool:
        NON_ENTITIES_PATTERN = re.compile(r"""
                            (wd:(?=[\s.}]))
                            |
                            (wd:[^Qq].*(?=[.}]))       
                            |             
                            (wd:[Qq][^\d]+(?=[.}]))
                            """, re.X)
        return NON_ENTITIES_PATTERN.search(query_string) is not None


class WikidataTemplate(Template):

    def __init__(self, query_string: Union[WikidataQuery, Query, str]):
        if isinstance(query_string, WikidataQuery) or isinstance(query_string, Query):
            query_string = str(query_string)
        self.query = WikidataQuery.normalized_query(query_string)

    @classmethod
    def get_query_template(cls, sparql_query: Query) -> str:
        return cls(sparql_query).get_empty_query(ignore_type=True)

    def get_empty_query(self, remove_properties: bool = False, ignore_type: bool = False, normalize: bool = False) -> str:
        """
        Given a query string, replaces wikidata entities for placeholder
        according to the Template's replace rules.

        :return: template query
        """
        entities = self.query.entities
        properties = self.query.properties
        query_string = str(self.query)
        type_entities = WikidataQueryPatternHelper.type_entities(query_string) if not ignore_type else list()
        added_entities = set()
        added_properties = set()
        QUERY_TRIPLES_PATTERN = WikidataQueryPatternHelper.get_query_triples_matches()
        query_triples = QUERY_TRIPLES_PATTERN.findall(query_string)
        for idx, case in enumerate(QUERY_TRIPLES_PATTERN.finditer(query_string), 1):
            for entity in set(entities):
                entity_name = str(entity)
                if entity_name in added_entities:
                    continue
                if entity_name in type_entities:
                    placeholder = '<type>' if len(type_entities) == 1 else f'<type_{type_entities.index(entity_name) + 1}>'
                    query_string, _ = re.subn(entity_name + '(?=[.\s}])', placeholder, query_string, count=int(normalize))
                    added_entities.add(entity_name) if not normalize else None
                if case.group('sbj') == entity_name:
                    query_string, _ = re.subn(entity_name + '(?=[.\s}])', f'<sbj_{idx}>', query_string, count=int(normalize))
                    added_entities.add(entity_name) if not normalize else None
                if case.group('obj') == entity_name:
                    query_string, _ = re.subn(entity_name + '(?=[.\s}])', f'<obj_{idx}>', query_string, count=int(normalize))
                    added_entities.add(entity_name) if not normalize else None
            if remove_properties:
                for w_property in properties:
                    property_name = str(w_property)
                    if property_name.lower() == 'wdt:p31' and (idx == 1 and len(query_triples) > 1 ):
                        if '<prop_type>' not in query_string:
                            query_string, _ = re.subn(property_name + '\s', '<prop_type> ', query_string,
                                                  count=int(normalize))
                        continue
                    if property_name in added_properties:
                        continue
                    if property_name in case.group('prop'):
                        query_string, _ = re.subn(property_name + '\s', f'<prop_{idx}> ', query_string, count=int(normalize))
                        added_properties.add(property_name) if not normalize else None
        query_string, _ = re.subn('<prop_type>', 'wdt:P31', query_string, count=int(normalize))
        query_string = WikidataQueryFixer.lcquad2_template_fix(query_string)
        query_string, _ = WikidataQueryPatternHelper.str_values_fix(query_string)
        query_string, _ = WikidataQueryPatternHelper.number_fix(query_string)
        query_string = WikidataQueryFixer.change_x_per_obj(query_string)
        query_string = WikidataQueryFixer.change_sub_per_sbj(query_string)
        query_string = WikidataQueryFixer.add_where_after_count(query_string)
        if normalize:
            query_string = WikidataQueryPatternHelper.unify_filter_op(query_string)
            query_string = WikidataQueryPatternHelper.unify_asc_desc_op(query_string)
            query_string = re.sub('<(\w+)_\d+>', '<\g<1>>', query_string)
        return query_string

    def get_base_template(self) -> str:
        return self.get_empty_query(remove_properties=True, ignore_type=True, normalize=True)

    def get_template(self) -> str:
        return self.get_empty_query(ignore_type=True)

    def get_slots(self, ignore_type=True) -> Dict[str, str]:
        """
        Given a query string, replaces wikidata entities for placeholder
        according to the Template's replace rules.

        :return: template query
        """
        entities = self.query.entities
        query_string = str(self.query)
        type_entities = WikidataQueryPatternHelper.type_entities(query_string) if not ignore_type else list()
        slot_dict = dict()
        added_entities = set()
        QUERY_TRIPLES_PATTERN = WikidataQueryPatternHelper.get_query_triples_matches()
        for idx, case in enumerate(QUERY_TRIPLES_PATTERN.finditer(query_string), 1):
            for entity in entities:
                entity_name = str(entity)
                if entity_name in added_entities:
                    continue
                if entity_name in type_entities:
                    slot = '<type>' if len(type_entities) == 1 else f'<type_{type_entities.index(entity_name) + 1}>'
                    query_string, _ = re.subn(entity_name + '(?=[.\s}])', slot, query_string)
                    slot_dict[entity_name] = slot
                    added_entities.add(entity_name)
                elif case.group('sbj') == entity_name:
                    query_string, _ = re.subn(entity_name + '(?=[.\s}])', f'<sbj_{idx}>', query_string)
                    slot_dict[entity_name] = f'<sbj_{idx}>'
                    added_entities.add(entity_name)
                elif case.group('obj') == entity_name:
                    query_string, _ = re.subn(entity_name + '(?=[.\s}])', f'<obj_{idx}>', query_string)
                    slot_dict[entity_name] = f'<obj_{idx}>'
                    added_entities.add(entity_name)
        query_string, str_value = WikidataQueryPatternHelper.str_values_fix(query_string)
        if str_value:
            slot_dict[str_value] = '<str_value>'
        query_string, number = WikidataQueryPatternHelper.number_fix(query_string)
        if number:
            slot_dict[number] = '<num>'
        return slot_dict

    def get_entity_slot_map(self) -> List[Dict]:
        return list(dict(slot=slot, entity=entity) for slot, entity in self.get_slots().items())

    def replace_entities(self, query_string: str) -> str:
        template = WikidataTemplate(query_string)
        return template.get_empty_query(ignore_type=True)

    def get_label_entity_list(self, normalized_question: str, query_string: str) -> List[Dict]:
        query = WikidataQuery.normalized_query(query_string)
        return list(dict(entity=str(entity), label='') for entity in set(query.entities))

    def get_slot_list(self, normalized_question: str, query_string: str) -> List[Dict]:
        template = WikidataTemplate(query_string)
        slots = template.get_slots()
        return list(dict(slot=slot, label=entity_name) for entity_name, slot in slots.items())

    @property
    def query_string(self) -> str:
        return str(self.query)

    @property
    def triples(self) -> List[QueryTriple]:
        QUERY_TRIPLES_PATTERN = WikidataQueryPatternHelper.get_query_triples_matches()
        return list(QueryTriple.from_match_obj(case) for case in QUERY_TRIPLES_PATTERN.finditer(self.query_string))
