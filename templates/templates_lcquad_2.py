import re
from collections import OrderedDict
from typing import Optional, Union, Dict, List

from query_tools import WIKIDATA_ENTITY_PATTERN
from templates.base_template import TemplateNotFound, Template
from templates.wikidata_template import WikidataTemplate

TemplateDict = OrderedDict()


class TemplateLCQUAD2(Template):
    def __init__(
            self,
            template_string: str,
            intent: str = '',
            replace_rules: Optional[OrderedDict] = None,
            name_entity_map: Optional[Dict[int, int]] = None,
            name_value_map: Optional[Dict[int, int]] = None,
            name_number_map: Optional[Dict[int, int]] = None,
            name_slot_map: Optional[Dict[int, int]] = None,
            to_be_fixed: bool = False,
            use_wikidata_template: bool = True
    ):
        """
        Represent a query template from the LC-QuaD 2 dataset .

        :param template_string: string identification
        :param replace_rules: replace rules for entity replacement
        :param name_entity_map: (label name, entity) dictionary for extract resources method
        :param name_value_map: (label name, string value) dictionary for extract resources method
        :param name_number_map: (label name, number) dictionary for extract resources method
        :param to_be_fixed:  query needs fix if True (only applies for RankMaxInstanceOfTypeTwoFacts)
        """
        self.template_string = template_string
        self.intent = intent
        self.replace_rules = replace_rules if replace_rules else OrderedDict()
        self.__name_entity_map = name_entity_map if name_entity_map else dict()
        self.__name_value_map = name_value_map if name_value_map else dict()
        self.__name_number_map = name_number_map if name_number_map else dict()
        self.name_slot_map = name_slot_map if name_slot_map else dict()
        self.to_be_fixed = to_be_fixed
        self.use_wikidata_template = use_wikidata_template

    @classmethod
    def create_template(cls, template_id: Union[str, int]) -> Optional['TemplateLCQUAD2']:
        """
        Given a template string (ex: E REF ?F) or a template id (if no template)
        identifies and return the corresponding Template class.

        Raise TemplateNotFound if template string or id is not found.

        :param template_id: template identification
        :return: Template object
        """
        template_string = template_id if type(template_id) == str else f"empty {template_id}"
        lower_string = template_string.lower().replace('`', '').strip()
        for template_type, TemplateClass in TemplateDict.items():
            if lower_string == template_type:
                return TemplateClass()
        raise TemplateNotFound(template_id, template_string)

    def replace_entities(self, query_string: str) -> str:
        """
        Given a query string, replaces wikidata entities for placeholder
        according to the Template's replace rules. Applies query fix if define.

        :param query_string: SPARQL query string
        :return:  modified SPARQL query string
        """
        if self.use_wikidata_template:
            return WikidataTemplate(query_string).get_empty_query(ignore_type=True)
        for pattern, repl in self.replace_rules.items():
            query_string = re.sub(pattern, repl, query_string)
        if self.to_be_fixed:
            return self.__fix_empty_query(query_string)
        return query_string

    def __fix_empty_query(self, query: str) -> str:
        """
        Apply fix to the given string query (only needed on RankMaxInstanceOfTypeTwoFacts class).

        :param query: query string
        :return: fixed query string
        """
        return query

    def extract_resources(self, nnqt: str, query_string: str) -> Dict[str, str]:
        """
        Identify and associate label in the normalized natural question with resources in the
        query string (like Wikidata entities, string values or numbers).

        :param nnqt: normalized natural question
        :param query_string: query string
        :return: dictionary with labels <-> resources pairs
        """
        names = re.findall(r"[{<]([^{]*?)[>}]", nnqt)
        entities = re.findall(r"\w+:Q[0-9]+", query_string)
        values = re.findall(r"'(.*?)'", query_string)
        numbers = re.findall(r"(\d+\.?\d*)", query_string)
        result = dict()
        for name_idx, entity_idx in self.__name_entity_map.items():
            if entity_idx < len(entities):
                result[names[name_idx]] = entities[entity_idx]
        for name_idx, value_idx in self.__name_value_map.items():
            if value_idx < len(values):
                result["value_" + names[name_idx].strip("'")] = values[value_idx]
        for name_idx, number_idx in self.__name_number_map.items():
            if number_idx < len(numbers):
                result["number_" + names[name_idx]] = numbers[number_idx]
        return result

    def get_label_entity_list(self, normalized_question: str, query_string: str) -> List[Dict]:
        """
        Finds all (label name, entities) pairs and returns dict.

        Use for the Dataset normalization pipeline process.

        :param normalized_question: normalized natural question
        :param query_string: SPARQL query string
        :return:
        """
        names = re.findall(r"[{<]([^{]*?)[>}]", normalized_question)
        entities = WIKIDATA_ENTITY_PATTERN.findall(query_string)
        result = list()
        for name_idx, entity_idx in self.__name_entity_map.items():
            if entity_idx < len(entities):
                result.append({
                    "label": names[name_idx],
                    "entity": entities[entity_idx]
                })
        return result

    def get_slot_list(self, nnqt: str, query_string: str) -> List[Dict]:
        """
        Identify and associate label in the normalized natural question with plceholders of the
        query template (like Wikidata entities, string values or numbers).

        :param nnqt: normalized natural question
        :param query_string: query string
        :return: dictionary with labels <-> placeholder
        """
        names = re.findall(r"[{<]([^{]*?)[>}]", nnqt)
        placeholders = re.findall(r"<[^<>]+?>", self.replace_entities(query_string))
        result = list()
        for name_idx, placeholder_idx in self.name_slot_map.items():
            if placeholder_idx < len(placeholders):
                result.append({
                    "slot": placeholders[placeholder_idx],
                    "label": names[name_idx].strip("'")
                })
        return result

    def __str__(self) -> str:
        return self.template_string

    def __hash__(self):
        return str(str)

    def base_template_query(self, alternative: bool):
        return ""

    def get_intent(self, alternative: bool = False) -> str:
        return self.intent


################################### TEMPLATE 1 ######################################################################


class SelectSubjectInstanceOfType(TemplateLCQUAD2):

    def __init__(self):
        replace_rules = OrderedDict()
        replace_rules[r"(\?\w+\swdt:P31\s)\w+:Q[0-9]+"] = r"\1<type>"
        replace_rules[r"(\?\w+\s.*\s)\w+:Q[0-9]+"] = r"\1<obj>"
        name_entity_map = {0: 1, 2: 0}
        name_slot_map = {0: 1, 2: 0}
        super().__init__(
            template_string="<?S P O ; ?S InstanceOf Type>",
            intent="select_subject_instance_of_type",
            replace_rules=replace_rules,
            name_entity_map=name_entity_map,
            name_slot_map=name_slot_map
        )

    def base_template_query(self, alternative):
        return "select distinct ?sbj where { " \
               "?sbj <direct_prop> <obj> . " \
               "?sbj wdt:P31 <type> }"


TemplateDict["<?s p o ; ?s instanceof type>"] = SelectSubjectInstanceOfType


################################### TEMPLATE 2.1 ######################################################################


class SelectSubjectInstanceOfTypeContainsWord(TemplateLCQUAD2):

    def __init__(self):
        replace_rules = OrderedDict()
        replace_rules[r"(\?\w+\swdt:P31\s)\w+:Q[0-9]+"] = r"\1<type>"
        replace_rules[r"lcase\((.*?)'\w+'\)"] = r"lcase(\1<label>)"
        name_entity_map = {0: 0}
        name_value_map = {1: 0}
        name_slot_map = {0: 0, 1: 1}
        super().__init__(
            template_string="<?S P O ; ?S instanceOf Type ; contains word >",
            intent="select_subject_instance_of_type_contains_word",
            replace_rules=replace_rules,
            name_entity_map=name_entity_map,
            name_value_map=name_value_map,
            name_slot_map=name_slot_map
        )

    def base_template_query(self, alternative):
        return "select distinct ?sbj ?sbj_label where { " \
               "?sbj wdt:P31 <type> . " \
               "?sbj rdfs:label ?sbj_label ." \
               "filter(contains(lcase(?sbj_label), <label>)) . " \
               "filter (lang(?sbj_label) = 'en') } limit 25"


TemplateDict["<?s p o ; ?s instanceof type ; contains word >"] = SelectSubjectInstanceOfTypeContainsWord


################################### TEMPLATE 2.2 ######################################################################


class SelectSubjectInstanceOfTypeStartsWith(TemplateLCQUAD2):

    def __init__(self):
        replace_rules = OrderedDict()
        replace_rules[r"(\?\w+\swdt:P31\s)\w+:Q[0-9]+"] = r"\1<type>"
        replace_rules[r"lcase\((.*?)'\w+'\)"] = r"lcase(\1<letter>)"
        name_entity_map = {0: 0}
        name_value_map = {1: 0}
        name_slot_map = {0: 0, 1: 1}
        super().__init__(
            template_string="<?S P O ; ?S instanceOf Type ; starts with character >",
            intent="select_subject_instance_of_type_starts_with",
            replace_rules=replace_rules,
            name_entity_map=name_entity_map,
            name_value_map=name_value_map,
            name_slot_map=name_slot_map
        )

    def base_template_query(self, alternative):
        return "select distinct ?sbj ?sbj_label where { " \
               "?sbj wdt:P31 <type> . ?sbj rdfs:label ?sbj_label . " \
               "filter(strstarts(lcase(?sbj_label), <letter>)) . " \
               "filter (lang(?sbj_label) = 'en') } limit 25 "


TemplateDict["<?s p o ; ?s instanceof type ; starts with character >"] = SelectSubjectInstanceOfTypeStartsWith


################################### TEMPLATE 3 ######################################################################


class SelectObjectInstanceOfType(TemplateLCQUAD2):

    def __init__(self):
        replace_rules = OrderedDict()
        replace_rules[r"(\?\w+\swdt:P31\s)\w+:Q[0-9]+"] = r"\1<type>"
        replace_rules[r"\w+:Q[0-9]+(\s.*\s\?\w+)"] = r"<sbj>\1"
        name_entity_map = {0: 1, 2: 0}
        name_slot_map = {0: 1, 2: 0}
        super().__init__(
            template_string="<S P ?O ; ?O instanceOf Type>",
            intent="select_object_instance_of_type",
            replace_rules=replace_rules,
            name_entity_map=name_entity_map,
            name_slot_map=name_slot_map
        )

    def base_template_query(self, alternative):
        return "select distinct ?obj where { " \
               "<sbj> <direct_prop> ?obj . " \
               "?obj wdt:P31 <type> }"


TemplateDict["<s p ?o ; ?o instanceof type>"] = SelectObjectInstanceOfType


################################### TEMPLATE 4 ######################################################################


class AskOneFact(TemplateLCQUAD2):

    def __init__(self):
        replace_rules = OrderedDict()
        replace_rules[r"\w+:Q[0-9]+(\s.*\s)\w+:Q[0-9]+"] = r"<sbj>\1<obj>"
        name_entity_map = {0: 0, 2: 1}
        name_slot_map = {0: 0, 2: 1}
        super().__init__(
            template_string="Ask (ent-pred-obj)",
            intent="ask_one_fact",
            replace_rules=replace_rules,
            name_entity_map=name_entity_map,
            name_slot_map=name_slot_map
        )

    def base_template_query(self, alternative):
        return "ask where { <sbj> <direct_prop> <obj> }"


TemplateDict["ask (ent-pred-obj)"] = AskOneFact


################################### TEMPLATE 4.1 ######################################################################


class AskOneFactWithFilter(TemplateLCQUAD2):

    def __init__(self):
        replace_rules = OrderedDict()
        replace_rules[r"\w+:Q[0-9]+(\s.*\s\?\w+)"] = r"<sbj>\1"
        NUM_PATTERN = re.compile("""
            (?P<obj>\?\w+)
            \s*
            (?P<op>[=<>])
            \s*
            (?P<num>-?\d+\.?\d*)
        """, re.X)
        replace_rules[NUM_PATTERN] = r"\g<obj> \g<op> <num>"
        name_entity_map = {1: 0}
        name_number_map = {3: -1}
        name_slot_map = {1: 0, 3: 1}
        super().__init__(
            template_string="ASK ?sbj ?pred ?obj filter ?obj = num",
            intent="ask_one_fact_with_filter",
            replace_rules=replace_rules,
            name_entity_map=name_entity_map,
            name_number_map=name_number_map,
            name_slot_map=name_slot_map
        )

    def base_template_query(self, alternative):
        return "ask where { <sbj> <direct_prop> ?obj filter(?obj [=|<|>] <num>) } "


TemplateDict["ask ?sbj ?pred ?obj filter ?obj = num"] = AskOneFactWithFilter


################################### TEMPLATE 5 ######################################################################


class AskTwoFacts(TemplateLCQUAD2):

    def __init__(self):
        replace_rules = OrderedDict()
        replace_rules[r"\w+:Q[0-9]+(\s.*\s)\w+:Q[0-9]+([\s.]+)\w+:Q[0-9]+(\s.*\s)\w+:Q[0-9]+"] = (
            r"<sbj>\1<obj_1>\2<sbj>\3<obj_2>"
        )
        name_entity_map = {0: 0, 2: 1, 3: 3}
        name_slot_map = {0: 0, 2: 1, 3: 3}
        super().__init__(
            template_string="Ask (ent-pred-obj1 . ent-pred-obj2)",
            intent="ask_two_facts",
            replace_rules=replace_rules,
            name_entity_map=name_entity_map,
            name_slot_map=name_slot_map
        )

    def base_template_query(self, alternative):
        return "ask where { <sbj> <direct_prop> <obj_1> . <sbj> <direct_prop> <obj_2> }"


TemplateDict["ask (ent-pred-obj1 . ent-pred-obj2)"] = AskTwoFacts


################################### TEMPLATE 6 ######################################################################


class SelectOneFactSubject(TemplateLCQUAD2):

    def __init__(self):
        replace_rules = OrderedDict()
        replace_rules[r"\w+:Q[0-9]+"] = r"<sbj>"
        name_entity_map = {1: 0}
        name_slot_map = {1: 0}
        super().__init__(
            template_string="E REF ?F",
            intent="select_one_fact_subject",
            replace_rules=replace_rules,
            name_entity_map=name_entity_map,
            name_slot_map=name_slot_map
        )

    def base_template_query(self, alternative):
        return "select distinct ?answer where { <sbj> <direct_prop> ?answer}"


TemplateDict["e ref ?f"] = SelectOneFactSubject


################################### TEMPLATE 7 ######################################################################


class SelectOneFactObject(TemplateLCQUAD2):

    def __init__(self):
        replace_rules = OrderedDict()
        replace_rules[r"\w+:Q[0-9]+"] = r"<obj>"
        name_entity_map = {1: 0}
        name_slot_map = {1: 0}
        super().__init__(
            template_string="?D RDE E",
            intent="select_one_fact_object",
            replace_rules=replace_rules,
            name_entity_map=name_entity_map,
            name_slot_map=name_slot_map
        )

    def base_template_query(self, alternative):
        return "select distinct ?answer where { ?answer <direct_prop> <obj>}"


TemplateDict["?d rde e"] = SelectOneFactObject


################################### TEMPLATE 8 ######################################################################


class SelectTwoAnswers(TemplateLCQUAD2):

    def __init__(self):
        replace_rules = OrderedDict()
        replace_rules[r"\w+:Q[0-9]+"] = r"<sbj>"
        name_entity_map = {2: 0}
        name_slot_map = {2: 0}
        super().__init__(
            template_string="select where (ent-pred-obj1 . ent-pred-obj2)",
            intent="select_two_answers",
            replace_rules=replace_rules,
            name_entity_map=name_entity_map,
            name_slot_map=name_slot_map
        )

    def base_template_query(self, alternative):
        return "select ?ans_1 ?ans_2 where { <sbj> <direct_prop_1> ?ans_1 . <sbj> <direct_prop_2> ?ans_2 }"


TemplateDict["select where (ent-pred-obj1 . ent-pred-obj2)"] = SelectTwoAnswers


################################### TEMPLATE 8 ######################################################################


class SelectTwoFactsSubjectObject(TemplateLCQUAD2):

    def __init__(self):
        replace_rules = OrderedDict()
        replace_rules[r"\w+:Q[0-9]+(\s.*\s)(?P<answer>\?\w+)([\s.]+)(?P=answer)(\s.*\s)\w+:Q[0-9]+"] = (
            r"<sbj_1>\1\g<answer>\3\g<answer>\4<obj_2>"
        )
        name_entity_map = {1: 0, 3: 1}
        name_slot_map = {1: 0, 3: 1}
        super().__init__(
            template_string="E REF ?F . ?F RFG G",
            intent="select_two_facts_subject_object",
            replace_rules=replace_rules,
            name_entity_map=name_entity_map,
            name_slot_map=name_slot_map
        )

    def base_template_query(self, alternative):
        return "select ?answer where { <sbj_1> <direct_prop_1> ?answer . ?answer <direct_prop_2> <obj_2>}"


TemplateDict["e ref ?f . ?f rfg g"] = SelectTwoFactsSubjectObject


################################### TEMPLATE 9.1 ######################################################################


class SelectTwoFactsRightSubject(TemplateLCQUAD2):

    def __init__(self):
        replace_rules = OrderedDict()
        replace_rules[r"\w+:Q[0-9]+(\s.*\s\?X)"] = r"<sbj_1>\1"
        name_entity_map = {2: 0}
        name_slot_map = {2: 0}
        super().__init__(
            template_string="E REF xF . xF RFG ?G",
            intent="select_two_facts_right_subject",
            replace_rules=replace_rules,
            name_entity_map=name_entity_map,
            name_slot_map=name_slot_map
        )

    def base_template_query(self, alternative):
        return "select ?answer where { <sbj_1> <direct_prop_1> ?X . ?X <direct_prop_2> ?answer}"


TemplateDict["e ref xf . xf rfg ?g"] = SelectTwoFactsRightSubject


################################### TEMPLATE 9.2 ######################################################################


class SelectTwoFactsLeftSubject(TemplateLCQUAD2):

    def __init__(self):
        replace_rules = OrderedDict()
        replace_rules[r"\w+:Q[0-9]+(\s.*\s\?X)"] = r"<sbj_1>\1"
        name_entity_map = {2: 0}
        name_slot_map = {2: 0}
        super().__init__(
            template_string="C RCD xD . xD RDE ?E",
            intent="select_two_facts_left_subject",
            replace_rules=replace_rules,
            name_entity_map=name_entity_map,
            name_slot_map=name_slot_map
        )

    def base_template_query(self, alternative):
        return "select ?answer where { <sbj_1> <direct_prop_1> ?X . ?X <direct_prop_2> ?answer}"


TemplateDict["c rcd xd . xd rde ?e"] = SelectTwoFactsLeftSubject


################################### TEMPLATE 10.1 ######################################################################


class CountOneFactSubject(TemplateLCQUAD2):

    def __init__(self):
        replace_rules = OrderedDict()
        replace_rules[r"(\?\w+\s.*\s)\w+:Q[0-9]+"] = r"\1<obj>"
        name_entity_map = {1: 0}
        name_slot_map = {1: 0}
        super().__init__(
            template_string="Count ent (ent-pred-obj)",
            intent="count_one_fact_subject",
            replace_rules=replace_rules,
            name_entity_map=name_entity_map,
            name_slot_map=name_slot_map
        )

    def base_template_query(self, alternative):
        return "select (count(?sub) AS ?value ) { ?sub <direct_prop> <obj> }"


TemplateDict["count ent (ent-pred-obj)"] = CountOneFactSubject


################################### TEMPLATE 10.2 ######################################################################


class CountOneFactObject(TemplateLCQUAD2):

    def __init__(self):
        replace_rules = OrderedDict()
        replace_rules[r"\w+:Q[0-9]+(\s.*\s\?\w+)"] = r"<sbj>\1"
        name_entity_map = {1: 0}
        name_slot_map = {1: 0}
        super().__init__(
            template_string="Count Obj (ent-pred-obj)",
            intent="count_one_fact_object",
            replace_rules=replace_rules,
            name_entity_map=name_entity_map,
            name_slot_map=name_slot_map
        )

    def base_template_query(self, alternative):
        return "select (count(?obj) AS ?value ) { <sbj> <direct_prop> ?obj }"


TemplateDict["count obj (ent-pred-obj)"] = CountOneFactObject


################################### TEMPLATE 11.1 ######################################################################


class SelectOneQualifierValueUsingOneStatementProperty(TemplateLCQUAD2):

    def __init__(self):
        replace_rules = OrderedDict()
        replace_rules[r"\w+:Q[0-9]+(\s.*?\s)(?P<id>\?\w+)(.*?)(?P=id)"] = r"<sbj_1>\1\g<id>\3\g<id>"
        replace_rules[r"(?P<id>\?\w+)(.*?)(?P=id)(\s.*\s)\w+:Q[0-9]+"] = r"\g<id>\2\g<id>\3<obj_2>"
        replace_rules[r"'[\d\w\s\-.+/\\]+?'"] = r"<str_value>"
        # replace_rules[r"'.+?'"] = r"<str_value>"
        name_entity_map = {1: 0, 3: 1}
        name_value_map = {3: 0}
        name_slot_map = {1: 0, 3: 1}
        super().__init__(
            template_string="(E pred ?Obj ) prop value",
            intent="select_one_qualifier_value_using_one_statement_property",
            replace_rules=replace_rules,
            name_entity_map=name_entity_map,
            name_value_map=name_value_map,
            name_slot_map=name_slot_map
        )

    def base_template_query(self, alternative):
        if alternative:
            return "select ?value where { " \
                   "<sbj_1> <prop_1> ?s . " \
                   "?s <prop_s_1> ?x filter(contains(?x,<str_value>)) . " \
                   "?s <prop_q> ?value}"
        else:
            return "select ?value where { " \
                   "<sbj_1> <prop_1> ?s . " \
                   "?s <prop_s_1> <obj_2> . " \
                   "?s <prop_q> ?value}"


TemplateDict["(e pred ?obj ) prop value"] = SelectOneQualifierValueUsingOneStatementProperty


################################### TEMPLATE 11.2 ######################################################################


class SelectObjectUsingOneStatementProperty(TemplateLCQUAD2):

    def __init__(self):
        replace_rules = OrderedDict()
        replace_rules[r"\w+:Q[0-9]+(\s.*\s\?\w+)"] = r"<sbj_1>\1"
        replace_rules[r"(\?\w+\s.*?\s)\w+:Q[0-9]+"] = r"\1<obj_3>"
        replace_rules[r"'[\d\w\s+-.\\]+?'"] = r"<str_value>"
        name_entity_map = {1: 0, 3: 1}
        name_value_map = {3: 0}
        name_slot_map = {1: 0, 3: 1}
        super().__init__(
            template_string="(E pred F) prop ?value",
            intent="select_object_using_one_statement_property",
            replace_rules=replace_rules,
            name_entity_map=name_entity_map,
            name_value_map=name_value_map,
            name_slot_map=name_slot_map
        )

    def base_template_query(self, alternative):
        if alternative:
            return "select ?obj where { <sbj_1> <prop_1> ?s . ?s <prop_s_1> ?obj . " \
                   "?s <prop_q> ?x filter(contains(?x,<str_value>)) }"
        else:
            return "select ?obj where { <sbj_1> <prop_1> ?s . ?s <prop_s_1> ?obj . " \
                   "?s <prop_q> <obj_3> }"


TemplateDict["(e pred f) prop ?value"] = SelectObjectUsingOneStatementProperty


################################### TEMPLATE 12 ######################################################################


class RankInstanceOfTypeOneFact(TemplateLCQUAD2):

    def __init__(self):
        replace_rules = OrderedDict()
        replace_rules[r"(\?\w+\swdt:P31\s)\w+:Q[0-9]+"] = r"\1<type>"
        name_entity_map = {0: 0}
        name_slot_map = {0: 0}
        super().__init__(
            template_string="?E is_a Type, ?E pred Obj  value. MAX/MIN (value)",
            intent="rank_instance_of_type_one_fact",
            replace_rules=replace_rules,
            name_entity_map=name_entity_map,
            name_slot_map=name_slot_map
        )

    def base_template_query(self, alternative):
        return "select ?ent where { ?ent wdt:P31 <type> . ?ent <direct_prop> ?obj } order by [asc|desc](?obj)limit 5 "


TemplateDict["?e is_a type, ?e pred obj  value. max/min (value)"] = RankInstanceOfTypeOneFact


################################### TEMPLATE 13.1 ######################################################################


class RankMaxInstanceOfTypeTwoFacts(TemplateLCQUAD2):

    def __init__(self):
        replace_rules = OrderedDict()
        replace_rules[r"(\?\w+\swdt:P31\s)\w+:Q[0-9]+"] = r"\1<type>"
        replace_rules[r"(\?\w+\s.*?\s)\w+:Q[0-9]+"] = r"\1<obj_3>"
        name_entity_map = {0: 0, 3: 1}
        name_slot_map = {0: 0, 3: 1}
        super().__init__(
            template_string="?E is_a Type. ?E pred Obj. ?E-secondClause value. MAX (value)",
            intent="rank_max_instance_of_type_two_facts",
            replace_rules=replace_rules,
            name_entity_map=name_entity_map,
            name_slot_map=name_slot_map,
            to_be_fixed=True
        )

    def _TemplateLCQUAD2__fix_empty_query(self, query_string: str) -> str:
        FIX_PATTERN = re.compile("""
        }
        \s+
        (?P<sbj>\?\w+)
        \s+
        (?P<prop>\w+:P\d+)
        \s+
        (?P<obj><[\w\d_]+?>)
        """, re.X)
        query_string = FIX_PATTERN.sub(". \g<sbj> \g<prop> \g<obj> }", query_string)
        return query_string

    def base_template_query(self, alternative):
        return "select ?ent where { ?ent wdt:P31 <type> . ?ent <direct_prop_1> ?obj . ?ent <direct_prop_2> <obj_3> " \
               "} order by desc(?obj)limit 5 "


TemplateDict["?e is_a type. ?e pred obj. ?e-secondclause value. max (value)"] = RankMaxInstanceOfTypeTwoFacts


################################### TEMPLATE 13.2 ######################################################################


class RankMinInstanceOfTypeTwoFacts(TemplateLCQUAD2):

    def __init__(self):
        replace_rules = OrderedDict()
        replace_rules[r"(\?\w+\swdt:P31\s)\w+:Q[0-9]+"] = r"\1<type>"
        replace_rules[r"(\?\w+\s.*?\s)\w+:Q[0-9]+"] = r"\1<obj_3>"
        name_entity_map = {0: 0, 3: 1}
        name_slot_map = {0: 0, 3: 1}
        super().__init__(
            template_string="?E is_a Type. ?E pred Obj. ?E-secondClause value. MIN (value)",
            intent="rank_min_instance_of_type_two_facts",
            replace_rules=replace_rules,
            name_entity_map=name_entity_map,
            name_slot_map=name_slot_map,
            to_be_fixed=True
        )

    def _TemplateLCQUAD2__fix_empty_query(self, query_string: str) -> str:
        FIX_PATTERN = re.compile("""
        }
        \s+
        (?P<sbj>\?\w+)
        \s+
        (?P<prop>\w+:P\d+)
        \s+
        (?P<obj><[\w\d_]+?>)
        """, re.X)
        query_string = FIX_PATTERN.sub(". \g<sbj> \g<prop> \g<obj> }", query_string)
        return query_string

    def base_template_query(self, alternative):
        return "select ?ent where { ?ent wdt:P31 <type> . ?ent <direct_prop_1> ?obj . ?ent <direct_prop_2> <obj_3> " \
               "} order by asc(?obj)limit 5 "


TemplateDict["?e is_a type. ?e pred obj. ?e-secondclause value. min (value)"] = RankMinInstanceOfTypeTwoFacts


################################### TEMPLATE 14 (Empty template 2) #####################################################


class SelectTwoQualifierValuesUsingOneStatementProperty(TemplateLCQUAD2):

    def __init__(self):
        replace_rules = OrderedDict()
        replace_rules[
            r"\w+:Q[0-9]+(\sp:)(?P<prop>P\w+\s)(\?\w+\s.*\s\?\w+\sps:)(?P=prop)\w+:Q[0-9]+"] = (
            r"<sbj_1>\1\g<prop>\3\g<prop><obj_2>"
        )
        name_entity_map = {2: 0, 4: 1}
        name_slot_map = {2: 0, 4: 1}
        super().__init__(
            template_string="(E pred ?Obj) prop value1 value2",
            intent="select_two_qualifier_values_using_one_statement_property",
            replace_rules=replace_rules,
            name_entity_map=name_entity_map,
            name_slot_map=name_slot_map
        )

    def base_template_query(self, alternative):
        return "select ?value1 ?value2 where { " \
               "<sbj_1> <prop_1> ?s . " \
               "?s <prop_s_1> <obj_2> . " \
               "?s <prop_q_1> ?value1 . " \
               "?s <prop_q_2> ?value2 }"


TemplateDict["empty 2"] = SelectTwoQualifierValuesUsingOneStatementProperty


################################### TEMPLATE 14.2 (Empty template 3) ###################################################


class SelectOneQualifierValueAndObjectUsingOneStatementProperty(TemplateLCQUAD2):

    def __init__(self):
        replace_rules = OrderedDict()
        replace_rules[r"\w+:Q[0-9]+(\s.*\s\?\w+)"] = r"<sbj_1>\1"
        name_entity_map = {1: 0}
        name_slot_map = {1: 0}
        super().__init__(
            template_string="(E pred F) prop value",
            intent="select_one_qualifier_value_and_object_using_one_statement_property",
            replace_rules=replace_rules,
            name_entity_map=name_entity_map,
            name_slot_map=name_slot_map
        )

    def base_template_query(self, alternative):
        return "select ?value1 ?obj where { " \
               "<sbj_1> <prop_1> ?s . " \
               "?s <prop_s_1> ?obj . " \
               "?s <prop_q_1> ?value1 . }"


TemplateDict["empty 3"] = SelectOneQualifierValueAndObjectUsingOneStatementProperty
