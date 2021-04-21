from typing import Dict, Optional, List

import requests

from dataset_tools import QuestionCase
from entity_linking.base_entitity_linking_system import EntityLinkingSystem, EntityLinkingDict

OPEN_TAPIOCA_URL = "https://opentapioca.org/api/annotate"


# TODO: add EntityMapper parameter
class OpenTapioca(EntityLinkingSystem):
    """
    Class for the Open Tapioca Entity Linking system.

    More details: https://opentapioca.org/
    """
    def __init__(self, endpoint_url: Optional[str] = None):
        """
        OpenTapioca class constructor. Use the OpenTapioca web service.

        :param endpoint_url: OpenTapioca API url.
        """
        super().__init__(endpoint_url if endpoint_url else OPEN_TAPIOCA_URL)

    def __str__(self):
        """
        Get the OpenTapioca system string representation.

        :return: string representation.
        """
        return 'Open Tapioca'

    def _request(self, params: Dict):
        """
        Perform a request to the OpenTapioca webservice given a set or parameters.

        :param params: query parameters.
        :return: request json response dict, None if there is no successful response.
        """
        res = requests.get(self._get_url(), params)
        res_json = res.json()
        return res_json

    def construct_query_params(self, question_string: str) -> Dict:
        """
        Given a question string, construct the web service parameters.

        :param question_string: question string.
        :return: query parameters dict.
        """
        return {'query': question_string}

    def get_entity_extracted(
            self, question_case: QuestionCase, num_entities_expected: Optional[int] = None
    ) -> List[Dict]:
        """
        Perform entity annotation over the given question case.
        Expected OpeTapioca format:
            entity_annotation = {
                'ini': 0,
                'fin': 6,
                'label': "Pedrito",
                'url': "wd:Q121",
                'score_list' : [
                    {
                        'value': 0.99,
                        'field_name': 'log_likelihood'
                    }
                ]
            }
        A number of maximum expected entities can be passed.
        If the given QuestionCase contains a question id, such id is ignored.

        :param question_case: QuestionCase instance.
        :param num_entities_expected: maximum number of entities expected.
        :return: list of entity annotations.
        """
        if not question_case.question_text:  # if empty text is provided
            return list()
        # construct web service parameters and get annotations
        question_string = question_case.question_text
        params = self.construct_query_params(question_string)
        results = self.get_response(params)
        # if not results, return empty list
        if not results:
            return list()
        # adapt annotations results to the desired output
        summary = list()
        for case in results["annotations"]:
            start, end = case["start"], case["end"]
            if not case['best_qid']:
                continue
            data = {
                "ini": start,
                "fin": end,
                "label": question_string[start:end],
                "url": case['best_qid'],
                "score_list": [
                    {
                        'value': case['log_likelihood'],
                        'field_name': 'log_likelihood'
                    }
                ]
            }
            summary.append(data)
        return summary


# add OpenTapioca to the EntityLinkingDict for the load_model method
EntityLinkingDict['open_tapioca'] = OpenTapioca
