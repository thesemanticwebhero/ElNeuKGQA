import re
from typing import Dict, Optional, List

import requests

from dataset_tools import QuestionCase
from .base_entitity_linking_system import EntityLinkingSystem, EntityLinkingDict
from mapping.mapper import MapEntitiesWikipediaToWikidata
from query_tools import WIKIDATA_ENDPOINT_URL

token = ""

TAGME_URL = "https://tagme.d4science.org/tagme/tag"

TAGME_WAT_URL = "https://wat.d4science.org/wat/tag/tag"


class BaseTagMe(EntityLinkingSystem):
    """
    Class for the Base TAGME Entity Linking system.
    """
    def __init__(self, endpoint_url: str, skip_mapping: bool = False):
        """
        Base TAGME class constructor.

        :param endpoint_url: system API url.
        :param skip_mapping: if True, skip mapping process to Wikidata resources.
        """
        entity_mapper = MapEntitiesWikipediaToWikidata(WIKIDATA_ENDPOINT_URL) if not skip_mapping else None
        super().__init__(endpoint_url, entity_mapper)

    def _request(self, params: Dict) -> Optional[Dict]:
        """
        Perform a request to the TAGME web service given a set or parameters.

        :param params: query parameters.
        :return: request json response dict, None if there is no successful response.
        """
        # headers = {'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
        res = requests.get(self._get_url(), params=params)  # , headers=headers
        res_json = res.json()
        return res_json

    def construct_query_params(self, question_string: str) -> Dict:
        """
        Given a question string, construct the web service parameters.

        :param question_string: question string.
        :return: query parameters dict.
        """
        return {'text': question_string, 'gcube-token': token, 'lang': 'en'}

    def get_entity_extracted(
            self, question_case: QuestionCase, num_entities_expected: Optional[int] = None
    ) -> List[Dict]:
        """
        Perform entity annotation over the given question case.
        Expected TAGME format:
            entity_annotation = {
                'ini': 0,
                'fin': 6,
                'label': "Pedrito",
                'url': "https://en.wikipedia.org/wiki/Pedrito",
                'score_list' : [
                    {
                        'value': 0.99,
                        'field_name': 'rho'
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
        params = self.construct_query_params(question_case.question_text)
        results = self.get_response(params)
        # if not results, return empty list
        if not results:
            return list()
        # adapt annotations results to the desired output
        summary = list()
        for case in results['annotations'] if 'annotations' in results else list():
            try:
                data = {
                    'ini': case['start'],
                    'fin': case['end'],
                    'label': case['spot'],
                    'url': 'wiki:' + re.sub(r'\s+', '_', case['title']),
                    'score_list': [
                        {
                            'value': case['rho'],
                            'field_name': 'rho'
                        }
                    ]
                }
                summary.append(data)
            except KeyError as e:  # usually a mention without annotation
                print(e)
                print(case)
        return self.map_summary(summary)


class TagMe(BaseTagMe):
    """
    Class for the TAGME Entity Linking system.

    More details: https://sobigdata.d4science.org/group/tagme/tagme-help
    """
    def __init__(self, endpoint_url: Optional[str] = None, skip_mapping: bool = False):
        """
        TAGME class constructor. Use the TAGME web service.

        :param endpoint_url: TAGME API url.
        :param skip_mapping: if True, skip mapping process to Wikidata resources.
        """
        endpoint_url = endpoint_url if endpoint_url else TAGME_URL
        super().__init__(endpoint_url, skip_mapping)

    def __str__(self):
        """
        Get the TAGME system string representation.

        :return: string representation.
        """
        return 'TAGME'


class TagMeWAT(BaseTagMe):
    """
    Class for the TAGME WAT Entity Linking system.

    More details: https://sobigdata.d4science.org/web/tagme/wat-api
    """
    def __init__(self, endpoint_url: Optional[str] = None, skip_mapping: bool = False):
        """
        TAGME WAT class constructor. Use the TAGME WAT web service.

        :param endpoint_url: TAGME WAT API url.
        :param skip_mapping: if True, skip mapping process to Wikidata resources.
        """
        endpoint_url = endpoint_url if endpoint_url else TAGME_WAT_URL
        super().__init__(endpoint_url, skip_mapping)

    def __str__(self):
        """
        Get the TAGME WAT system string representation.

        :return: string representation.
        """
        return 'TAGME_WAT'


# add TagMe to the EntityLinkingDict for the load_model method
EntityLinkingDict['TAGME'] = TagMe
# add TagMeWAT to the EntityLinkingDict for the load_model method
EntityLinkingDict['tagme_wat'] = TagMeWAT
