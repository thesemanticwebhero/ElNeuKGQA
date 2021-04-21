from typing import Optional


class BaseCaseMethodNotImplemented(Exception):
    """
    Exception when a BaseCase method has not been implemented.
    """
    pass


class BaseCase:
    """
    Base class for representing a dataset case with a mandatory question text
    and an optional question id and sparql query answer.
    """
    @property
    def question_id(self) -> Optional[int]:
        """
        Get the question id, if exists.

        :return: question integer identifier or None if there is no identifier.
        """
        return None

    @property
    def question_text(self) -> str:
        """
        Get the question text.

        :exception: BaseCaseMethodNotImplemented if method has not been implemented.
        :return: question string.
        """
        raise BaseCaseMethodNotImplemented

    @property
    def sparql_query(self) -> Optional[str]:
        """
        Get the SPARQL query answer.

        :return: SPARQL query string or None if there is no SPARQL query answer.
        """
        return None


class QuestionCase(BaseCase):
    """
    Question case class for representing a dataset question case with
    a mandatory question text and an optional question id. No SPARQL query answer required.
    """
    def __init__(self, question_text: str, question_id: Optional[int] = None):
        """
        Question case constructor.

        :param question_text: question case string.
        :param question_id: question case identifier.
        """
        self.__id = question_id
        self.__text = question_text

    @property
    def question_id(self) -> Optional[int]:
        """
        Get the question id, if exists.

        :return: question integer identifier or None if there is no identifier.
        """
        return self.__id

    @property
    def question_text(self) -> str:
        """
        Get the question text.

        :return: question string.
        """
        return self.__text


class Question(QuestionCase):
    """
    Question class for representing a question case that only requires a question text.
    No question id nor SPARQL query answer required.
    """

    def __init__(self, question_text: str):
        """
        Question constructor.

        :param question_text: question case string.
        """
        super().__init__(question_text)
