from typing import Optional, Tuple, Dict

from dataset_tools import QuestionCase
from filenames import SlotFillingFiles
from neural_sparql_machine.fairseq_wrapper import FairseqTranslator
from entity_linking import BaseEntityLinkingSystem
from query_generation import SparqlQueryGenerator, QueryTemplateGenerator, \
    FairseqQueryTemplateGenerator
from query_tools import Query, WikidataQuery, WikidataTokenizer
from question_answering.base_question_answering_system import BaseQuestionAnsweringSystem
from slot_filling import StandardQueryGenerationSlotFillingHelper, \
    BaseQueryGenerationSlotFillingHelper, SlotFillingMethodEnum
from slot_filling.slot_filler import BaseSlotFiller, FlairNerSlotFiller
from templates.wikidata_template import WikidataTemplate


class QueryGeneratorNotFound(Exception):
    """
    Exception when a Query Generator instance is not found.
    """
    pass


class NeuralQuestionAnsweringSystem(BaseQuestionAnsweringSystem):
    """
    Question Answering system based on Neural Machine Translation for generating SPARQL queries.
    """

    def __init__(self, query_generator: SparqlQueryGenerator):
        """
        Neural Question Answering constructor.

        :param query_generator: Neural Machine Translation query generator.
        """
        self.query_generator = query_generator

    def get_query(self, question_case: QuestionCase, num_entities_expected: Optional[int] = None) -> Optional[WikidataQuery]:
        """
        Given a question string, obtain the query that should retrieve the answers.

        :param question_case: question string.
        :param num_entities_expected: maximum number of entities expected.
        :return: Wikidata Query, if exists.
        """
        sparql_query = self.query_generator.generate_one(question_case)
        return sparql_query if str(sparql_query) else None

    def get_query_debug(self, question_case: QuestionCase, num_entities_expected: Optional[int] = None) -> Tuple[Optional[WikidataQuery], Dict]:
        """
        Given a question string, obtain the query that should retrieve the answers.
        Includes a debug dict with entities identified and the query template, for analysis purposes.

        :param question_case: question string.
        :param num_entities_expected: maximum number of entities expected.
        :return: tuple with Wikidata Query (if exists), and its debug dict.
        """
        # query_prediction = self.get_query(question_case)
        sparql_query_candidates = self.query_generator.generate_one_n_candidates(question_case)
        if not sparql_query_candidates:
            query_prediction = None
        else:
            query_prediction = WikidataQuery(str(sparql_query_candidates[0]))
        debug = {
            'entities': None,
            'slots': None,
            'query_templates': [
                WikidataTemplate(query).get_empty_query(ignore_type=True) for query in sparql_query_candidates
            ],
            'sparql_queries': sparql_query_candidates
        }
        return query_prediction, debug

    @classmethod
    def load_model(cls, question_answering_opt: Dict, dataset_opt: Optional[Dict]):
        print("Loading SPARQL Query Generator system...")
        return cls(SparqlQueryGenerator.load_model(question_answering_opt['query_generator_opt'], dataset_opt))


class EntityLinkingQuestionAnsweringSystem(BaseQuestionAnsweringSystem):
    """
    Question Answering system based on Neural Machine Translation and Entity Linking for generating SPARQL queries.
    """

    def __init__(self, query_template_generator: QueryTemplateGenerator, entity_linker: BaseEntityLinkingSystem,
                 slot_filler: BaseSlotFiller, slot_filling_method: Optional[BaseQueryGenerationSlotFillingHelper] = None):
        """
        Entity Linking Question Answering constructor.

        :param query_template_generator: Neural Machine Translation query template generator.
        :param entity_linker: Entity linking system for entity recognition and disambiguation.
        :param slot_filler: Slot Filling system for named entity labeling.
        """
        self.query_template_generator = query_template_generator
        self.entity_linker = entity_linker
        self.slot_filler = slot_filler
        self.filler_method = slot_filling_method if slot_filling_method else StandardQueryGenerationSlotFillingHelper()

    def get_query(self, question_case: QuestionCase, num_entities_expected: Optional[int] = None) -> Optional[
        WikidataQuery]:
        """
        Given a question string, obtain the query that should retrieve the answers.

        :param question_case: question string.
        :param num_entities_expected: maximum number of entities expected.
        :return: Wikidata Query, if exists.
        """
        entities = self.entity_linker.get_entity_extracted(question_case, num_entities_expected)
        slots = self.slot_filler.evaluate(question_case)
        query_template_candidates = self.query_template_generator.generate_one_n_candidates(question_case)
        for query_template in query_template_candidates:
            slots_dict = {case['label']: case['slot'] for case in slots}
            query_string, _ = self.filler_method.fill_template(query_template, slots_dict, entities)
            sparql_query = WikidataQuery(query_string)
            if sparql_query.is_valid():
                return sparql_query
        return None

    def get_query_debug(self, question_case: QuestionCase, num_entities_expected: Optional[int] = None) -> Tuple[
        Query, Dict]:
        """
        Given a question string, obtain the query that should retrieve the answers.
        Includes a debug dict with entities identified and the query template, for analysis purposes.
        The uid parameter is used for an offline Entity Linking process over known datasets.

        :param question_case: question string.
        :param num_entities_expected: maximum number of entities expected.
        :return: tuple with Wikidata Query (if exists), and its debug dict.
        """
        entities = self.entity_linker.get_entity_extracted(question_case, num_entities_expected)
        slots = self.slot_filler.evaluate(question_case)
        query_template_candidates = self.query_template_generator.generate_one_n_candidates(question_case)
        # Create sparql candidates
        sparql_query_candidates = list()
        slot_entity_map_candidates = list()
        for query_template in query_template_candidates:
            slots_dict = {case['label']: case['slot'] for case in slots}
            query_string, slot_entity_map = self.filler_method.fill_template(str(query_template), slots_dict, entities)
            sparql_query = WikidataQuery(query_string)
            sparql_query_candidates.append(sparql_query)
            slot_entity_map_candidates.append(slot_entity_map)
        return sparql_query_candidates[0] if sparql_query_candidates else None, {'entities': entities, 'slots': slots,
                                                                                 'query_templates': query_template_candidates,
                                                                                 'sparql_queries': sparql_query_candidates,
                                                                                 'slot_entity_map': slot_entity_map_candidates}

    @classmethod
    def create_fairseq_model(cls, vocab: str, checkpoints_folder: str, entity_linker: BaseEntityLinkingSystem):
        """
        Construct a Entity Linking Neural Question Answering system based
        on the FairseqTranslator class to generate SPARQL queries and the Flair Slot Filler.

        :param vocab: vocab path file of the Fairseq Translator
        :param checkpoints_folder: model folder of the Fairseq Translator
        :param entity_linker: Entity linking system for entity recognition and disambiguation.
        :return:
        """
        # Initialize query template generator
        translator = FairseqTranslator(vocab, checkpoints_folder)
        query_template_generator = FairseqQueryTemplateGenerator(translator, WikidataTokenizer())
        # Initialize slot filler
        file_manager = SlotFillingFiles(dataset_variant='plus')
        slot_filler = FlairNerSlotFiller(model_folder=file_manager.model_folder())
        return cls(query_template_generator, entity_linker, slot_filler)

    @classmethod
    def load_model(cls, question_answering_opt: Dict, dataset_opt: Dict):
        # Initialize Entity Linking system
        entity_linking_opt = question_answering_opt['entity_linking_opt']
        print("Building Entity Linking system...")
        entity_linker = BaseEntityLinkingSystem.load_model(entity_linking_opt, dataset_opt)
        # Initialize Slot Filler system
        print("Loading Slot Filling system...")
        slot_filler_opt = question_answering_opt['slot_filler_opt']
        slot_filler = BaseSlotFiller.load_model(slot_filler_opt, dataset_opt)
        filler_helper = SlotFillingMethodEnum[slot_filler_opt['filling_method']].value()
        print(f"{slot_filler_opt['filling_method']} filling method...")
        # Initialize Query Template generator
        print("Loading Query Template Generator system...")
        query_template_generator_opt = question_answering_opt['query_template_generator_opt']
        query_template_generator = QueryTemplateGenerator.load_model(query_template_generator_opt, dataset_opt)
        return cls(query_template_generator, entity_linker, slot_filler, filler_helper)
