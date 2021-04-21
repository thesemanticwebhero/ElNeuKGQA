import json
import subprocess
import urllib.parse

from typing import Dict, Optional, List

from dataset_tools import QuestionCase
from entity_linking.base_entitity_linking_system import EntityLinkingSystem, EntityLinkingDict
from mapping.mapper import MapEntitiesWikipediaToWikidata
from query_tools import WIKIDATA_ENDPOINT_URL

AIDA_URL = "https://gate.d5.mpi-inf.mpg.de/aida/service/disambiguate"


class Aida(EntityLinkingSystem):
    """
    Class for the AIDA Entity Linking system.

    More details: https://www.mpi-inf.mpg.de/departments/databases-and-information-systems/research/ambiverse-nlu/aida
    """
    def __init__(self, endpoint_url: Optional[str] = None, skip_mapping: bool = False):
        """
        AIDA class constructor. Use the AIDA web service.

        :param endpoint_url: AIDA API url.
        :param skip_mapping: if True, skip mapping process to Wikidata resources.
        """
        endpoint_url = endpoint_url if endpoint_url else AIDA_URL
        entity_mapper = MapEntitiesWikipediaToWikidata(WIKIDATA_ENDPOINT_URL) if not skip_mapping else None
        super().__init__(endpoint_url, entity_mapper)

    def __str__(self):
        """
        Get the AIDA system string representation.

        :return: string representation.
        """
        return 'Aida'

    def _request(self, params: Dict) -> Optional[Dict]:
        """
        Perform a request to the AIDA web service given a set or parameters.

        :param params: query parameters.
        :return: request json response dict, None if there is no successful response.
        """
        my_json = None
        try:
            query_post = "text=" + urllib.parse.quote(params['text'])
            p = subprocess.Popen(['curl', '--data', query_post, self._get_url()], stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
            if stdout:
                my_json = stdout.decode('utf8')  # .replace("'", '"')
                return json.loads(my_json)
        except Exception as e:
            print(my_json)
            raise e
        return None

    def construct_query_params(self, question_string: str) -> Dict:
        """
        Given a question string, construct the web service parameters.

        :param question_string: question string.
        :return: query parameters dict.
        """
        return {'text': question_string}

    @staticmethod
    def _decode(encoded_string):
        """
        Decode a unicode string.

        Example: "Joe_Jackson_\\u0028manager\\u0029" -> "Joe_Jackson_(manager)"

        :param encoded_string: unicode string.
        :return: decoded string.
        """
        return urllib.parse.unquote(encoded_string.replace("\\u00", "%"))

    def _yago_to_wikipedia(self, yago_uri):
        """
        Convert YAGO uri to a Wikipedia uri.

        :param yago_uri: yago uri.
        :return: wikipedia uri string.
        """
        return "https://en.wikipedia.org/wiki/" + self._decode(yago_uri.split(":")[1])

    def get_entity_extracted(
            self, question_case: QuestionCase, num_entities_expected: Optional[int] = None
    ) -> List[Dict]:
        """
        Perform entity annotation over the given question case.
        Expected AIDA format:
            entity_annotation = {
                'ini': 0,
                'fin': 6,
                'label': "Pedrito",
                'url': "https://en.wikipedia.org/wiki/Pedrito",
                'score_list' : [
                    {
                        'value': 0.99,
                        'field_name': 'disambiguationScore'
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
        for case in results['mentions'] if 'mentions' in results else list():
            try:
                start = int(case["offset"])
                end = int(case["offset"]) + int(case["length"])
                data = {
                    'ini': start,
                    'fin': end,
                    'label': question_string[start:end],
                    'url': self._yago_to_wikipedia(case["bestEntity"]["kbIdentifier"]),
                    'score_list': [
                        {
                            'value': float(case["bestEntity"]['disambiguationScore']),
                            'field_name': 'disambiguationScore'
                        }
                    ]
                }
                summary.append(data)
            except KeyError:  # usually a mention without annotation
                continue
        return self.map_summary(summary)


# add Aida to the EntityLinkingDict for the load_model method
EntityLinkingDict['aida'] = Aida
