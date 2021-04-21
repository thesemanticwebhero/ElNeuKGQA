from pathlib import Path
from typing import List, Dict

from dataset_tools import QuestionCase
from filenames import QueryTemplateGenerationFiles
from neural_sparql_machine.fairseq_wrapper import FairseqTranslator
from query_generation.base_query_generator import BaseQueryGenerator
from query_generation.sparql_query_generator import FairseqSparqlQueryGenerator, \
    OfflineSparqlQueryGenerator, SparqlQueryGenerator
from query_tools import Tokenizer, WikidataTokenizer
from templates.wikidata_template import WikidataTemplate

QueryTemplateDict = dict()


class QueryTemplateGenerator(BaseQueryGenerator):
    """
    Query Template Generator class for generating Query Templates given a Natural Language question.
    """
    def __init__(self, query_generator: SparqlQueryGenerator):
        """
        Fairseq QueryTemplateGenerator Constructor. Follows the same structure as a SparqlQueryGenerator.

        :param query_generator: SPARQL query generator.
        """
        self.query_generator = query_generator

    def generate_one(self, question_case: QuestionCase) -> str:
        """
        Given a QuestionCase instance, generate a Query Template.

        :param question_case: natural language QuestionCase instance.
        :return: a Query Template string.
        """
        return str(self.query_generator.generate_one(question_case))

    def generate_one_n_candidates(self, question_case: QuestionCase, n_candidates: int = 5) -> List[str]:
        """
        Given a QuestionCase instance, generate n Query Template candidates.

        :param question_case: natural language QuestionCase instance.
        :param n_candidates: number of candidates per question.
        :return: a List of Query Template strings which represents the candidates for the given question.
        """
        return list(
            str(query) for query in self.query_generator.generate_one_n_candidates(question_case, n_candidates))

    def generate(self, question_cases: List[QuestionCase]) -> List[str]:
        """
        Given a list of QuestionCase instance, generate a Query template for each question.

        :param question_cases: list of natural language QuestionCase instance.
        :return: a List of Query Template strings whose elements represent the output for each question respectively.
        """
        return list(self.generate_one(question_string) for question_string in question_cases)

    def generate_n_candidates(
            self, question_cases: List[QuestionCase], n_candidates: int = 5
    ) -> List[List[str]]:
        """
        Given a list of QuestionCase instance, generate n Query template candidates for each question.

        :param question_cases: list of natural language QuestionCase instance.
        :param n_candidates: number of candidates per question.
        :return: a List of Lists Query Template strings. Each List represent the candidates of each question respectively.
        """
        return list(self.generate_one_n_candidates(q_string, n_candidates) for q_string in question_cases)

    @classmethod
    def load_model(cls, query_template_opt: Dict, dataset_opt: Dict) -> 'QueryTemplateGenerator':
        """
        TODO: documentation

        :param query_template_opt:
        :param dataset_opt:
        :return:
        """
        system_name = query_template_opt["system_name"]
        if query_template_opt['offline']:
            file_manager = QueryTemplateGenerationFiles(**dataset_opt['params'])
            offline_results = file_manager.output_file(system_name)
            print(f'Using offline data from "{offline_results}"...')
            query_template_generator = OfflineQueryTemplateGenerator(offline_results)
        else:
            system_type = query_template_opt["system_type"]
            query_template_generator = QueryTemplateDict[system_type].load_model(query_template_opt, dataset_opt)
        print(f"{system_name} system ready...")
        return query_template_generator


class FairseqQueryTemplateGenerator(QueryTemplateGenerator):
    """
    Query Template Generator class for generating Query Templates given a Natural Language question.
    Based on Fairseq Neural Translation models.

    More details: https://fairseq.readthedocs.io/en/latest/
    """
    def __init__(self, translation_model: FairseqTranslator, query_tokenizer: Tokenizer):
        """
        Fairseq QueryTemplateGenerator Constructor.

        :param translation_model: Neural Machine Translation fairseq model wrapper.
        :param query_tokenizer: Tokenizer for decoding the SPARQl query output from the query generator.
        """
        super().__init__(FairseqSparqlQueryGenerator(translation_model, query_tokenizer))

    @classmethod
    def load_model(cls, query_template_opt: Dict, dataset_opt: Dict) -> 'FairseqQueryTemplateGenerator':
        assert 'system_params' in query_template_opt
        file_manager = QueryTemplateGenerationFiles(**query_template_opt['system_params'])
        translator_params = dict(
            vocab_path=file_manager.vocab_folder(),
            checkpoints_folder=file_manager.model_folder(),
            checkpoint_file=query_template_opt[
                'checkpoint_file'] if 'checkpoint_file' in query_template_opt else None,
            gpu=query_template_opt['gpu'] if 'gpu' in query_template_opt else False
        )
        translator = FairseqTranslator(**translator_params)
        return FairseqQueryTemplateGenerator(translator, WikidataTokenizer())


class OfflineQueryTemplateGenerator(QueryTemplateGenerator):
    """
    Offline Query Template Generator class for a generating Query Template given a Natural Language question.
    Use results gathered for other QueryTemplateGenerator's
    """
    def __init__(self, offline_results: Path):
        """
        Offline SparqlQueryGenerator Constructor.

        :param offline_results: ...
        """
        super().__init__(OfflineSparqlQueryGenerator(offline_results))


class FairseqBaselineQueryTemplateGenerator(QueryTemplateGenerator):
    """
    Query Template Generator class for generating Query Templates given a Natural Language question.
    Based on Fairseq Neural Translation models and WikidataTemplate.

    More details: https://fairseq.readthedocs.io/en/latest/
    """
    def __init__(self, query_generator: FairseqSparqlQueryGenerator):
        """
        Fairseq QueryTemplateGenerator Constructor.

        :param query_generator: Fairseq SPARQL query generator.
        """
        super().__init__(query_generator)

    def generate_one(self, question_case: QuestionCase) -> str:
        """
        Given a QuestionCase instance, generate a SPARQL query.

        :param question_case: natural language QuestionCase instance.
        :return: a SPARQL Query instance.
        """
        sparql_query = self.query_generator.generate_one(question_case)
        return WikidataTemplate.get_query_template(sparql_query)

    def generate_one_n_candidates(self, question_case: QuestionCase, n_candidates: int = 5) -> List[str]:
        """
        Given a QuestionCase instance generate n SPARQL query candidates.

        :param question_case: natural language QuestionCase instance.
        :param n_candidates: number of candidates per question.
        :return: a List of SPARQL Query instance which represents the candidates for the given question.
        """
        assert n_candidates > 0
        sparql_queries = self.query_generator.generate_one_n_candidates(question_case, n_candidates)
        return list(WikidataTemplate.get_query_template(candidate) for candidate in sparql_queries)

    @classmethod
    def load_model(cls, query_template_opt: Dict, dataset_opt: Dict) -> 'FairseqBaselineQueryTemplateGenerator':
        generator = FairseqSparqlQueryGenerator.load_model(query_template_opt, dataset_opt)
        return FairseqBaselineQueryTemplateGenerator(generator)


QueryTemplateDict['Fairseq'] = FairseqQueryTemplateGenerator
QueryTemplateDict['Baseline'] = FairseqBaselineQueryTemplateGenerator
