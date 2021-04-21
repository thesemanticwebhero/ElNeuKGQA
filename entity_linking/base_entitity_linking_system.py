import time
from typing import Dict, Optional, List

from dataset_tools import QuestionCase
from filenames import EntityLinkingFiles
from mapping.mapper.entity_mapper import EntityMapperToWikidata
from query_tools import Resource


class BaseEntityLinkingSystemMethodNotImplemented(Exception):
    """
    Exception when a BaseEntityLinkingSystem method hasn't been implemented yet.
    """
    pass


# Entity Linking Dict for the BaseEntityLinkingSystem load_model method.
EntityLinkingDict = dict()


class BaseEntityLinkingSystem:
    """
    Base class for a Entity Linking system.
    """
    def __str__(self):
        """
        Get the string representation. Usually the system name.

        :return: Entity Linking system string representation.
        """
        raise BaseEntityLinkingSystemMethodNotImplemented

    def get_entity_extracted(
            self, question_case: QuestionCase, num_entities_expected: Optional[int] = None
    ) -> List[Dict]:
        """
        Perform entity annotation over the given question case.
        Expected format:
            entity_annotation = {
                'ini': 0,
                'fin': 6,
                'label': "Pedrito",
                'url': "wd:Q121",
                'score_list' : [
                    {
                        'value': 0.99,
                        'field_name': 'my_score'
                    }, ...
                ]
            }
        A number of maximum expected entities can be passed.

        :param question_case: QuestionCase instance.
        :param num_entities_expected: maximum number of entities expected.
        :return: list of entity annotations.
        """
        raise BaseEntityLinkingSystemMethodNotImplemented

    @classmethod
    def load_model(cls, entity_linking_opt: Dict, dataset_opt: Optional[Dict] = None) -> 'BaseEntityLinkingSystem':
        """
        Given a Entity Linking options and Dataset options, build the Entity linking model according to the given options.

        Expected Entity Linking options:
            system_name: str = EntityLinkingDict key.
            offline: bool = If True, set offline settings. Need to provide a results_folder value.
            results_folder: Path = for an online setting, folder name where to retrieve results.
            fixed_result: bool = If True, return the number of expected entities according to the benchmark (experiment purposes).
            system_params: Dict = parameters for the class constructor of the chosen model.

        Expected Dataset options:
            params: Dict = input parameters for the EntityLinking FileManager class
            only_test: bool = If True, only execute test cases (experiment purposes)

        :param entity_linking_opt: Entity Linking system parameter options.
        :param dataset_opt: Dataset parameter options.
        :return: BaseEntityLinkingSystem instance.
        """
        # if offline setting, retrieve joined results (ComposedEntityLinkingSystem)
        if entity_linking_opt['offline']:
            file_manager = EntityLinkingFiles(**dataset_opt['params'])
            joined_dataset_output = file_manager.output_file('joined')
            print(f'Using offline data from "{joined_dataset_output}"...')
            entity_linking_opt['system_params']['joined_results'] = joined_dataset_output
        # Build Entity Linking model
        entity_linker = EntityLinkingDict[entity_linking_opt['system_type']](**entity_linking_opt['system_params'])
        print(f"{entity_linker} system ready...")
        return entity_linker


class EntityLinkingSystem(BaseEntityLinkingSystem):
    """
    Base class for a individual Entity Linking system. Usually is a system based on a API web service.
    If the annotations of the service are not Wikidata URIs, an EntityMapper can be used to map to Wikidata resources.
    """
    def __init__(self, endpoint_url: str, entity_mapper: Optional[EntityMapperToWikidata] = None):
        """
        EntityLinkingSystem class constructor.

        If a value for the entity_mapper field is not passed, the system do not perform entity mapping.

        :param endpoint_url: API endpoint url string.
        :param entity_mapper: optional EntityMapperToWikidata instance.
        """
        self.__endpoint_url = endpoint_url
        self.entity_mapper = entity_mapper

    def _get_url(self) -> str:
        """
        Get the endpoint url string.

        :return: endpoint url string.
        """
        return self.__endpoint_url

    def _request(self, params: Dict) -> Optional[Dict]:
        """
        Perform a request to the webservice given a set or parameters.

        :param params: query parameters.
        :return: request response dict, None if there is no successful response.
        """
        raise BaseEntityLinkingSystemMethodNotImplemented

    def construct_query_params(self, question_string: str) -> Dict:
        """
        Given a question string, construct the web service parameters.

        :param question_string: question string.
        :return: query parameters dict.
        """
        raise BaseEntityLinkingSystemMethodNotImplemented

    def get_response(self, params: Dict, max_retries: int = 3, sleep_time: int = 60) -> Optional[Dict]:
        """
        Perform request to webservice with a maximum amount of retries.

        :param params: query parameters.
        :param max_retries: maximum amount of retries.
        :param sleep_time: sleep time (in seconds) between tries.
        :return: request response dict, None if there is no successful response.
        """
        for retry in range(1, max_retries + 1):
            try:
                return self._request(params)
            except Exception as e:
                print(e)
            sleep_time = retry * sleep_time
            print(f"Retry #{retry} in {sleep_time}s")
            time.sleep(sleep_time)
        print(f"[{self._get_url()}] Max amount of retries ({max_retries}) reached")
        print("params: ", params)
        return None

    def map_summary(self, cases: List[Dict]) -> List[Dict]:
        """
        Given entity annotations, perform URI mapping (if EntityMapper is provided).

        :param cases: entity annotations dict.
        :return: list of mapped entity annotations.
        """
        if not self.entity_mapper:
            return cases
        entities = {Resource.create_resource(case['url']) for case in cases}
        mapped_entities = self.entity_mapper.map_resource_batches(entities)
        final_summary = list()
        for case in cases:
            system_entity = Resource.create_resource(case['url'])
            if system_entity in mapped_entities:
                mapped_case = dict(case)
                mapped_case['url'] = str(mapped_entities[system_entity][0][1])
                final_summary.append(mapped_case)
        return final_summary
