from typing import Optional, Tuple, Dict

from SPARQLWrapper.SPARQLExceptions import QueryBadFormed

from dataset_tools import QuestionCase
from query_tools import Query, QueryHelper, WIKIDATA_ENDPOINT_URL


class BaseQuestionAnsweringSystemMethodNotImplemented(Exception):
    """
    Exception when a BaseQuestionAnsweringSystem method hasn't been implemented yet.
    """
    pass


class BaseQuestionAnsweringSystem:
    """
    Base class for a Question Answering system.
    """

    def get_query_answers_pair(
            self, question_case: QuestionCase, endpoint_url: Optional[str] = None,
            num_entities_expected: Optional[int] = None
    ) -> Tuple[Optional[Query], Optional[Dict]]:
        """
        Given a QuestionCase instance, obtain the SPARQL query, and execute it
        on the given KB endpoint (Wikidata by default) to retrieve the answers.

        :param question_case: QuestionCase instance.
        :param endpoint_url: optional endpoint url where to perform the SPARQL query.
        :param num_entities_expected: maximum number of entities expected.
        :return: a tuple with a Query and an answer Dict, if exists.
        """
        query = self.get_query(question_case, num_entities_expected)
        query_helper = QueryHelper(endpoint_url if endpoint_url else WIKIDATA_ENDPOINT_URL)
        try:
            return query, query_helper.do_query(query) if query else None
        except QueryBadFormed:
            return query, None

    def get_query(self, question_case: QuestionCase, num_entities_expected: Optional[int] = None) -> Optional[Query]:
        """
        Given a QuestionCase instance, obtain the query that should retrieve the answers.

        :param question_case: QuestionCase instance.
        :param num_entities_expected: maximum number of entities expected.
        :return: Query, if exists.
        """
        raise BaseQuestionAnsweringSystemMethodNotImplemented

    def get_answers(self, question_case: QuestionCase, endpoint_url: Optional[str] = None,
                    num_entities_expected: Optional[int] = None) -> Optional[Dict]:
        """
        Given a QuestionCase instance, obtain the answers of that question.

        :param question_case: QuestionCase instance.
        :param endpoint_url: optional endpoint url where to query.
        :param num_entities_expected: maximum number of entities expected.
        :return: answer Dict, if exists.
        """
        return self.get_query_answers_pair(question_case, endpoint_url, num_entities_expected)[1]

    def get_query_debug(self, question_case: QuestionCase, num_entities_expected: Optional[int] = None) -> Tuple[
        Optional[Query], Dict]:
        """
        Given a QuestionCase instance, obtain the query that should retrieve the answers.
        Includes debug information for analysis purposes

        :param question_case: QuestionCase instance.
        :param num_entities_expected: maximum number of entities expected.
        :return: tuple with (Query, if exists) and dict with debug info.
        """
        raise BaseQuestionAnsweringSystemMethodNotImplemented

    @classmethod
    def load_model(cls, **kargs):
        raise BaseQuestionAnsweringSystemMethodNotImplemented
