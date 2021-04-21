from typing import Optional, Dict, List

from dataset_tools.dataset_case.base_case import BaseCase, QuestionCase, Question


class NormalizedCase(BaseCase):
    """
    Class for representing a normalized case which includes a mandatory question text
    and might include:
        - Question id
        - SPARQL query answer.
        - Entities included in the SPARQL query with the corresponding label in the question text.
        - Query template with placeholders deduced from the SPARQL query answer.
        - Slots that includes the mapping entity label -> query placeholder.
    """
    def __init__(self, case: Dict):
        """
        NormalizedCase class constructor.
        The case dict have to contain al least the question text.

        :param case: normalized case dictionary.
        """
        self.case = case

    @property
    def question_id(self) -> Optional[int]:
        """
        Get the question id, if exists.

        :exception: AssertionError if the question case id is not an integer.
        :return: question integer identifier or None if there is no identifier.
        """
        if 'question_id' not in self.case:
            return None
        assert type(self.case['question_id']) == int
        return self.case['question_id']

    @property
    def question_text(self) -> str:
        """
        Get the question text.

        :exception: AssertionError if the question text is not included.
        :exception: AssertionError if the question case text is not an string.
        :return: question string.
        """
        assert 'natural_language_question' in self.case
        assert type(self.case['natural_language_question']) == str
        return self.case['natural_language_question']

    def __get_query_answer_dict(self) -> Optional[Dict]:
        """
        Obtain query answer dict that should contain the SPARQL query, entities, slots and query template.
        If exists.

        :exception: AssertionError if the query answer field is not a list.
        :exception: AssertionError if the question answer first element is not a dict.
        :return: query answer dict, None if there is no query answer dict.
        """
        if 'query_answer' not in self.case or not self.case['query_answer']:
            return None
        assert type(self.case['query_answer']) == list
        assert type(self.case['query_answer'][0]) == dict
        return self.case['query_answer'][0]

    @property
    def sparql_query(self) -> Optional[str]:
        """
        Get the SPARQL query answer.

        :exception: AssertionError if the sparql_query field is not in the query_answer_dict
        :exception: AssertionError if the SPARQL query is not a string.
        :return: SPARQL query string or None if there is no SPARQL query answer.
        """
        query_answer_dict = self.__get_query_answer_dict()
        if not query_answer_dict:
            return None
        assert 'sparql_query' in query_answer_dict
        assert type(query_answer_dict['sparql_query']) == str
        return query_answer_dict['sparql_query']

    @property
    def question_case(self) -> QuestionCase:
        """
        Return a QuestionCase instance with the question id and question text.

        :return: QuestionCase instance.
        """
        return QuestionCase(self.question_text, self.question_id)

    @property
    def question(self) -> Question:
        """
        Return a Question instance with the question text.

        :return: Question instance.
        """
        return Question(self.question_text)

    @property
    def entities(self) -> Optional[List[Dict]]:
        """
        Return entities included in the SPARQL query with the corresponding label in the question text.
        The format of each case is the following:
        entities = [
            {
                'label': 'Pedrito',
                'entity': 'wd:Q121'
            }, ...
        ]

        :exception: AssertionError if the entities are not a list. The format of each case is not checked.
        :return: entity case list, None if is not included.
        """
        query_answer_dict = self.__get_query_answer_dict()
        if not query_answer_dict or 'entities' not in query_answer_dict:
            return None
        assert type(query_answer_dict['entities']) == list
        return query_answer_dict['entities']

    @property
    def slots(self) -> Optional[List[Dict]]:
        """
        Return slots that includes the mapping entity label -> query template placeholder.
        The format of each case is the following:
        slots = [
            {
                'label': 'Pedrito',
                'slot': '<sbj_1>'
            }, ...
        ]

        :exception: AssertionError if the slots are not a list. The format of each case is not checked.
        :return: slot case list, None if is not included.
        """
        query_answer_dict = self.__get_query_answer_dict()
        if not query_answer_dict or 'slots' not in query_answer_dict:
            return None
        assert type(query_answer_dict['slots']) == list
        return query_answer_dict['slots']

    @property
    def query_template(self) -> Optional[str]:
        """
        Return query template with placeholders deduced from the SPARQL query answer.

        :exception: AssertionError if the query template is not a string.
        :return: query template string or None if is not included.
        """
        query_answer_dict = self.__get_query_answer_dict()
        if not query_answer_dict or 'sparql_template' not in query_answer_dict:
            return None
        assert type(query_answer_dict['sparql_template']) == str
        return query_answer_dict['sparql_template']

    @property
    def answers(self) -> Optional[Dict]:
        """
        Return query binding answers from the SPARQL query answer.

        :exception: AssertionError if the query template is not a string.
        :return: binding answers dict or None if is not included.
        """
        query_answer_dict = self.__get_query_answer_dict()
        if not query_answer_dict or 'answers' not in query_answer_dict or query_answer_dict['answers'] is None:
            return None
        assert type(query_answer_dict['answers']) == dict
        return query_answer_dict['answers']