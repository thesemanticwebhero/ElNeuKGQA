import re
import unicodedata


class Normalizer:

    @staticmethod
    def unicode_to_ascii(string: str) -> str:
        """
        Turn a Unicode string to plain ASCII, thanks to
        http://stackoverflow.com/a/518232/2809427

        :param string:
        :return:
        """
        return ''.join(
            c for c in unicodedata.normalize('NFD', string)
            if unicodedata.category(c) != 'Mn'
        )

    @staticmethod
    def normalize_question(question_string: str) -> str:
        """
        Lowercase, trim, and remove non-letter characters

        :param question_string:
        :return:
        """
        question_string = Normalizer.unicode_to_ascii(question_string.lower().strip())
        # string = re.sub(r"([.!])", r" \1", string)
        question_string = re.sub(r"[^a-zA-Z0-9]+", r" ", question_string)
        question_string = re.sub('s{2, }', ' ', question_string)
        return question_string.strip()

    @staticmethod
    def normalize_sparql_query(query_string: str) -> str:
        """
        Lowercase, trim, and remove non-letter characters

        :param query_string:
        :return:
        """
        query_string = Normalizer.unicode_to_ascii(query_string.lower().strip())
        # string = re.sub(r"([.!])", r" \1", string)
        query_string = re.sub(r"[^a-zA-Z0-9_]+", r" ", query_string)
        query_string = re.sub('s{2, }', ' ', query_string)
        return query_string.strip()