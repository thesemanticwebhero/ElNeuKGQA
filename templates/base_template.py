from typing import List, Dict


class TemplateNotFound(Exception):
    pass


class TemplateMethodNotImplemented(Exception):
    pass


class Template:

    def question_is_from_template(self, question: str) -> bool:
        raise TemplateMethodNotImplemented

    def query_is_from_template(self, query: str) -> bool:
        raise TemplateMethodNotImplemented

    def replace_entities(self, query: str) -> str:
        raise TemplateMethodNotImplemented

    def get_label_entity_list(self, question: str, query: str) -> List[Dict]:
        raise TemplateMethodNotImplemented

    def get_slot_list(self, nnqt: str, query_string: str) -> List[Dict]:
        raise TemplateMethodNotImplemented


class QuestionNotMatched(Exception):
    pass


class QueryNotMatched(Exception):
    pass


class TemplateNotValid(Exception):
    pass