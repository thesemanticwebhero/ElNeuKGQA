import json
from pathlib import Path
from typing import List, Dict, Optional

from dataset_tools import Normalizer, QuestionCase
from filenames import QueryGenerationFiles
from neural_sparql_machine.fairseq_wrapper import FairseqTranslator
from query_generation import BaseQueryGenerator, BaseQueryGeneratorMethodNotImplemented
from query_tools import Query, Tokenizer, WikidataQuery, WikidataTokenizer

QueryGenerationDict = dict()


class SparqlQueryGenerator(BaseQueryGenerator):
    """
    SPARQL Query Generator class for generating SPARQL queries given a Natural Language question.
    """
    def generate_one(self, question_case: QuestionCase) -> Query:
        """
        Given a QuestionCase instance, generate a SPARQL query.

        :param question_case: natural language QuestionCase instance.
        :return: a SPARQL Query instance.
        """
        raise BaseQueryGeneratorMethodNotImplemented

    def generate_one_n_candidates(self, question_case: QuestionCase, n_candidates: int = 5) -> List[Query]:
        """
        Given a QuestionCase instance generate n SPARQL query candidates.

        :param question_case: natural language QuestionCase instance.
        :param n_candidates: number of candidates per question.
        :return: a List of SPARQL Query instance which represents the candidates for the given question.
        """
        raise BaseQueryGeneratorMethodNotImplemented

    def generate(self, question_cases: List[QuestionCase]) -> List[Query]:
        """
        Given a list of QuestionCase instance generate a SPARQL query for each question.

        :param question_cases: list of natural language QuestionCase instance.
        :return: a List of SPARQL Query instances whose elements represent the output for each question respectively.
        """
        raise BaseQueryGeneratorMethodNotImplemented

    def generate_n_candidates(self, question_cases: List[QuestionCase], n_candidates: int = 5) -> List[List[Query]]:
        """
        Given a list of QuestionCase instance, generate n SPARQL query candidates for each question.

        :param question_cases: list of natural language QuestionCase instance.
        :param n_candidates: number of candidates per question.
        :return: a List of Lists of SPARQL Query instances. Each List represent the candidates of each question respectively.
        """
        raise BaseQueryGeneratorMethodNotImplemented

    @classmethod
    def load_model(cls, query_generator_opt: Dict, dataset_opt: Dict) -> 'SparqlQueryGenerator':
        # initialize Query Generation file manager
        system_name = query_generator_opt["system_name"]
        if query_generator_opt['offline']:
            file_manager = QueryGenerationFiles(**dataset_opt['params'])
            offline_results = file_manager.output_file(system_name)
            print(f'Using offline data from "{offline_results}"...')
            query_generator = OfflineSparqlQueryGenerator(offline_results)
        else:
            system_type = query_generator_opt["system_type"]
            query_generator = QueryGenerationDict[system_type].load_model(query_generator_opt, dataset_opt)
        print(f"{system_name} system ready...")
        return query_generator


class FairseqSparqlQueryGenerator(SparqlQueryGenerator):
    """
    SPARQL Query Generator class for a generating SPARQL query given a Natural Language question.
    Based on Fairseq Neural Translation models.

    More details: https://fairseq.readthedocs.io/en/latest/
    """
    def __init__(self, translation_model: FairseqTranslator, query_tokenizer: Tokenizer):
        """
        Fairseq SparqlQueryGenerator Constructor.

        :param translation_model: Neural Machine Translation fairseq model wrapper.
        :param query_tokenizer: Tokenizer for decoding the SPARQl query output from the query generator.
        """
        self.translation_model = translation_model
        self.query_tokenizer = query_tokenizer

    def generate_one(self, question_case: QuestionCase) -> Query:
        """
        Given a QuestionCase instance, generate a SPARQL query.

        :param question_case: natural language QuestionCase instance.
        :return: a SPARQL Query instance.
        """
        question_string = question_case.question_text
        normalized_question = Normalizer.normalize_question(question_string)
        return self.query_tokenizer.decode(self.translation_model.evaluate([normalized_question])[0])

    def generate_one_n_candidates(self, question_case: QuestionCase, n_candidates: int = 5) -> List[Query]:
        """
        Given a QuestionCase instance generate n SPARQL query candidates.

        :param question_case: natural language QuestionCase instance.
        :param n_candidates: number of candidates per question.
        :return: a List of SPARQL Query instance which represents the candidates for the given question.
        """
        assert n_candidates > 0
        question_string = question_case.question_text
        normalized_question = Normalizer.normalize_question(question_string)
        candidates = self.translation_model.evaluate_best_n(normalized_question, beam=n_candidates)
        return list(self.query_tokenizer.decode(candidate) for candidate in candidates)

    def generate(self, question_cases: List[QuestionCase]) -> List[Query]:
        """
        Given a list of QuestionCase instance generate a SPARQL query for each question.

        :param question_cases: list of natural language QuestionCase instance.
        :return: a List of SPARQL Query instances whose elements represent the output for each question respectively.
        """
        return list(self.generate_one(question_case) for question_case in question_cases)

    def generate_n_candidates(self, question_cases: List[QuestionCase], n_candidates: int = 5) -> List[List[Query]]:
        """
        Given a list of QuestionCase instance, generate n SPARQL query candidates for each question.

        :param question_cases: list of natural language QuestionCase instance.
        :param n_candidates: number of candidates per question.
        :return: a List of Lists of SPARQL Query instances. Each List represent the candidates of each question respectively.
        """
        assert n_candidates > 0
        return list(self.generate_one_n_candidates(q_case, n_candidates) for q_case in question_cases)

    @classmethod
    def load_model(cls, query_generator_opt: Dict, dataset_opt: Dict) -> 'FairseqSparqlQueryGenerator':
        """
        TODO: documentation

        :param query_generator_opt:
        :param dataset_opt:
        :return:
        """
        assert 'system_params' in query_generator_opt
        file_manager = QueryGenerationFiles(**query_generator_opt['system_params'])
        translator_params = dict(
            vocab_path=file_manager.vocab_folder(),
            checkpoints_folder=file_manager.model_folder(),
            checkpoint_file=query_generator_opt['checkpoint_file'] if 'checkpoint_file' in query_generator_opt else None,
            gpu=query_generator_opt['gpu'] if 'gpu' in query_generator_opt else False
        )
        translator = FairseqTranslator(**translator_params)
        return FairseqSparqlQueryGenerator(translator, WikidataTokenizer())


class OfflineSparqlQueryGenerator(SparqlQueryGenerator):
    """
    Offline SPARQL Query Generator class for a generating SPARQL query given a Natural Language question.
    Use results gathered for other SparqlQueryGenerator's
    """
    def __init__(self, offline_results: Path):
        """
        Offline SparqlQueryGenerator Constructor.

        :param offline_results: ...
        """
        self.offline_results = offline_results
        with open(offline_results, encoding='utf-8') as inJsonFile:
            data = json.load(inJsonFile)
            self.uid_data_map = {case['uid']: case for case in data['questions']}

    def generate_one(self, question_case: QuestionCase) -> Query:
        """
        Given a QuestionCase instance, generate a SPARQL query.

        :param question_case: natural language QuestionCase instance.
        :return: a SPARQL Query instance.
        """
        question_id = question_case.question_id
        if question_id not in self.uid_data_map:
            print(f"Warning: {question_id} is not in cache. You might want to update your results.")
            return WikidataQuery("")
        result_case = self.uid_data_map[question_id]
        return WikidataQuery(result_case['system_answer'][0])

    def generate_one_n_candidates(self, question_case: QuestionCase, n_candidates: int = 5) -> List[Query]:
        """
        Given a QuestionCase instance generate n SPARQL query candidates.

        :param question_case: natural language QuestionCase instance.
        :param n_candidates: number of candidates per question.
        :return: a List of SPARQL Query instance which represents the candidates for the given question.
        """
        question_id = question_case.question_id
        if question_id not in self.uid_data_map:
            print(f"Warning: {question_id} is not in cache. You might want to update your results.")
            return list()
        result_case = self.uid_data_map[question_id]
        candidates_length = min(n_candidates, len(result_case))
        return list(WikidataQuery(query) for query in result_case['system_answer'][:candidates_length])

    def generate(self, question_cases: List[QuestionCase]) -> List[Query]:
        """
        Given a list of QuestionCase instance generate a SPARQL query for each question.

        :param question_cases: list of natural language QuestionCase instance.
        :return: a List of SPARQL Query instances whose elements represent the output for each question respectively.
        """
        return list(self.generate_one(question_case) for question_case in question_cases)

    def generate_n_candidates(self, question_cases: List[QuestionCase], n_candidates: int = 5) -> List[List[Query]]:
        """
        Given a list of QuestionCase instance, generate n SPARQL query candidates for each question.

        :param question_cases: list of natural language QuestionCase instance.
        :param n_candidates: number of candidates per question.
        :return: a List of Lists of SPARQL Query instances. Each List represent the candidates of each question respectively.
        """
        return list(self.generate_one_n_candidates(q_case, n_candidates) for q_case in question_cases)

    @classmethod
    def load_model(cls, query_generator_opt: Dict, dataset_opt: Optional[Dict] = None) -> 'OfflineSparqlQueryGenerator':
        raise BaseQueryGeneratorMethodNotImplemented


QueryGenerationDict['Fairseq'] = FairseqSparqlQueryGenerator