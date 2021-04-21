from typing import Dict, Optional, List

import requests
from requests.exceptions import ConnectionError as requestConnectionError

from dataset_tools import QuestionCase
from entity_linking.base_entitity_linking_system import EntityLinkingSystem, EntityLinkingDict
from mapping.mapper import MapEntitiesDBpediaToWikidata
from query_tools import WIKIDATA_ENDPOINT_URL

DBPEDIA_SPOTLIGHT_URL = "http://api.dbpedia-spotlight.org/en/annotate"


class DBpediaSpotlight(EntityLinkingSystem):
    """
    Class for the DBpedia Spotlight Entity Linking system.

    More details: https://www.dbpedia-spotlight.org/
    """
    def __init__(self, endpoint_url: Optional[str] = None, skip_mapping: bool = False):
        """
        DBpediaSpotlight class constructor. Use the DBpedia Spotlight web service.

        :param endpoint_url: DBpediaSpotlight API url.
        :param skip_mapping: if True, skip mapping process to Wikidata resources.
        """
        endpoint_url = endpoint_url if endpoint_url else DBPEDIA_SPOTLIGHT_URL
        entity_mapper = MapEntitiesDBpediaToWikidata(WIKIDATA_ENDPOINT_URL) if not skip_mapping else None
        super().__init__(endpoint_url, entity_mapper)

    def __str__(self):
        """
        Get the DBpedia Spotlight system string representation.

        :return: string representation.
        """
        return 'DBpedia Spotlight'

    def _request(self, params: Dict) -> Optional[Dict]:
        """
        Perform a request to the DBpedia Spotlight web service given a set or parameters.

        :param params: query parameters.
        :return: request json response dict, None if there is no successful response.
        """
        headers = {'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
        res = None
        try:
            res = requests.get(self._get_url(), params, headers=headers)
            res_json = res.json()
        except requestConnectionError:  # if the DBpedia web service shutdowns
            return None
        except Exception as e:
            print(res)
            raise e
        return res_json

    def construct_query_params(self, question_string: str) -> Dict:
        """
        Given a question string, construct the web service parameters.

        :param question_string: question string.
        :return: query parameters dict.
        """
        return {'text': question_string, 'confidence': 0.2, 'support': 20}

    def get_entity_extracted(
            self, question_case: QuestionCase, num_entities_expected: Optional[int] = None
    ) -> List[Dict]:
        """
        Perform entity annotation over the given question case.
        Expected DBpedia Spotlight format:
            entity_annotation = {
                'ini': 0,
                'fin': 6,
                'label': "Pedrito",
                'url': "http://dbpedia.org/resource/Pedrito",
                'score_list' : [
                    {
                        'value': 0.99,
                        'field_name': '@similarityScore'
                    },
                    {
                        'value': 0.51,
                        'field_name': '@percentageOfSecondRank'
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
        for case in results['Resources'] if 'Resources' in results else list():
            try:
                start = int(case['@offset'])
                label = case['@surfaceForm']
                data = {
                    'ini': start,
                    'fin': start + len(label),
                    'label': label,
                    'url': case['@URI'],
                    'score_list': [
                        {
                            'value': float(case['@similarityScore']),
                            'field_name': '@similarityScore'
                        },
                        {
                            'value': float(case['@percentageOfSecondRank']),
                            'field_name': '@percentageOfSecondRank'
                        }
                    ]
                }
                summary.append(data)
            except KeyError:  # usually a mention without annotation
                continue
        return self.map_summary(summary)


# add DBpediaSpotlight to the EntityLinkingDict for the load_model method
EntityLinkingDict['dbpedia_spotlight'] = DBpediaSpotlight
