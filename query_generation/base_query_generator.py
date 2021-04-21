from typing import List, Union

from dataset_tools import QuestionCase
from query_tools import Query


class BaseQueryGeneratorMethodNotImplemented(Exception):
    """
    Exception when a BaseQueryGenerator method hasn't been implemented yet.
    """
    pass


class BaseQueryGenerator:
    """
    Base Query Generator class for generating SPARQL queries or Query templates given a Natural Language question.
    """

    def generate_one(self, question_case: QuestionCase) -> Union[str, Query]:
        """
        Given a QuestionCase instance, generate a SPARQL query or Query template.

        :param question_case: QuestionCase instance.
        :return: a SPARQL Query instance or Query Template.
        """
        raise BaseQueryGeneratorMethodNotImplemented

    def generate_one_n_candidates(self, question_case: QuestionCase, n_candidates: int = 5) -> Union[List[str], List[Query]]:
        """
        Given a QuestionCase instance, generate n SPARQL query candidates or n Query template candidates.

        :param question_case: QuestionCase instance.
        :param n_candidates: number of candidates per question.
        :return: a List of SPARQL Query instance or a List of Query Template which represents the candidates for the given question.
        """
        raise BaseQueryGeneratorMethodNotImplemented

    def generate(self, question_cases: List[QuestionCase]) -> Union[List[str], List[Query]]:
        """
        Given a list of QuestionCase instances, generate a SPARQL query or Query template for each question.

        :param question_cases: list of QuestionCase instances.
        :return: a List of SPARQL Query instance or a List of Query Template whose elements represent the output for each question respectively.
        """
        raise BaseQueryGeneratorMethodNotImplemented

    def generate_n_candidates(
            self, question_cases: List[QuestionCase], n_candidates: int = 5
    ) -> Union[List[List[str]], List[List[Query]]]:
        """
        Given a list of QuestionCase instances, generate n SPARQL query candidates
        or n Query template candidates for each question.

        :param question_cases: list of QuestionCase instances.
        :param n_candidates: number of candidates per question.
        :return: a List of Lists of SPARQL Query instance or Query Template (not both). Each List represent the candidates of each question respectively.
        """
        raise BaseQueryGeneratorMethodNotImplemented
