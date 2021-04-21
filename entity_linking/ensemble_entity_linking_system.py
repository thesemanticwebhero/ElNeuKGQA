import json
import re
from pathlib import Path
from typing import Optional, List, Union, Dict, Set

from dataset_tools import QuestionCase
from entity_linking import BaseEntityLinkingSystem, OpenTapioca, DBpediaSpotlight, TagMe, Aida
from entity_linking.base_entitity_linking_system import EntityLinkingSystem, EntityLinkingDict
from query_tools import WIKIDATA_ENTITY_PATTERN

MAX_THRESHOLD = 100


class EnsembleEntityLinkingSystem(BaseEntityLinkingSystem):
    """
    Base class for Composed Entity Linking systems.
    It combines individual Entity Linking systems to enhance the performance in the Entity Linking task.
    """

    def __init__(self, joined_results: Optional[Union[Path, str]] = None, offline: bool = False):
        """
        Base ComposedEntityLinkingSystem class constructor.

        :param joined_results: offline joined results from individual Entity Linking systems. If no joined results
        are provided, the system performs a default online setting.
        :param offline: if True, the offline setting is used. It needs a joined_results value to be provided.
        """
        assert not offline or (offline and joined_results is not None)
        if joined_results:
            with open(joined_results, encoding='utf-8') as inJsonFile:
                data = json.load(inJsonFile)
                self.uid_data = {case['uid']: case for case in data['questions']}
        else:
            self.uid_data = dict()
        self.offline = offline
        self.systems: List[EntityLinkingSystem] = [Aida(), OpenTapioca(), TagMe(), DBpediaSpotlight()]

    def gather_results(self, question_case: QuestionCase) -> Dict:
        """
        Expected output format:
        {
            'uid': null,
            'text': text,
            'annotations': [
                {
                    'system': ...,
                    'output': [entity_annotations]
                }, ...
            ]
        }
        :param question_case: QuestionCase instance.
        :return: dictionary with joined annotations.
        """
        # if offline setting, retrieve data from joined results
        if self.offline:
            merged_data: Dict = self.uid_data.get(question_case.question_id, dict())
        # otherwise, retrieve annotations for each system web service.
        else:
            question_string = question_case.question_text
            merged_data: Dict = dict(uid=None, text=question_string, annotations=list())
            for system in self.systems:
                results = system.get_entity_extracted(question_case)
                merged_data['annotations'].append(dict(system=str(system), output=results))
        # if merged_data is not empty
        if merged_data:
            for case in merged_data["annotations"]:
                system = case['system']
                for output in case['output']:
                    # compress entity URI
                    entity_name = output['url'] if 'wd:' in output['url'] else ('wd:' + output['url'])
                    # if score is not provided, build one based on the Wikidata identifier, or just the entity name
                    if 'score_list' not in output:
                        output['score'] = int(re.match(r'Q(\d+)', entity_name).group(1)) \
                            if re.match(r'Q(\d+)', entity_name) else entity_name
                    # if the system is DBpedia Spotlight, reverse the percentOfSecondRank score
                    elif str(system) == 'DBpedia Spotlight':
                        score = output['score_list'][1]  # choosing percentOfSecondRank
                        output['score'] = -float(score['value'])
                    # otherwise, just cast value to float
                    else:
                        score = output['score_list'][0]
                        output['score'] = float(score['value'])
        return merged_data


class FullSystems(EnsembleEntityLinkingSystem):
    """
    Composed Entity Linking system that return all the gathered entities without any filter.
    It includes an oracle mode which, given the expected answer, only returns the correct answers and fill with
    dummy entities for the answers that are not found.
    """

    def __init__(self, joined_results: Optional[Union[Path, str]] = None, oracle: bool = False):
        """
        FullSystems class constructor.

        :param joined_results: offline joined results from individual Entity Linking systems.
        :param oracle: if True, the oracle setting is set on.
        """
        super().__init__(joined_results=joined_results, offline=joined_results is not None)
        self.oracle = oracle

    def __str__(self):
        """
        Return system string representation.

        :return: string representation.
        """
        return 'Full System'

    def _valid_entity(self, entity_name: str, found_uris: Set[str], expected_entities: List[str]) -> bool:
        """
        Return True if the given entity name is valid to be added to the final output annotations.
        An entity is valid if satisfy the following conditions:
            (1) entity is a Wikidata entity
            (2) entity has not been found
            (3) and entity is an expected answer while oracle setting is on

        :param entity_name: entity name string.
        :param found_uris: URIs found so far (to avoid duplicates).
        :param expected_entities: expected entities for the oracle setting.
        :return: True if entity is valid
        """
        return re.match(WIKIDATA_ENTITY_PATTERN, entity_name) and (  # (1)
                entity_name not in found_uris) and (  # (2)
                       not self.oracle or entity_name in expected_entities)  # (3)

    def get_entity_extracted(
            self, question_case: QuestionCase, num_entities_expected: Optional[int] = None
    ) -> List[Dict]:
        """
        Perform entity annotation over the given question case.
        A number of maximum expected entities can be passed.

        :param question_case: QuestionCase instance.
        :param num_entities_expected: maximum number of entities expected.
        :return: list of entity annotations.
        """
        # gather offline results or perform joined entity annotation
        results = self.gather_results(question_case)
        # if not results, return empty list
        if not results:
            return list()
        # adapt annotations results to the desired output
        summary = list()
        found_uris = set()
        # for oracle setting, retrieve expected entity URIs
        expected_entities = results['entities'] if 'entities' in results else list()
        for case in results["annotations"]:
            for output in case['output']:
                # compress Wikidata Entity URI
                entity_name = output['url'] if 'wd:' in output['url'] else ('wd:' + output['url'])
                # add only if entity is valid
                if self._valid_entity(entity_name, found_uris, expected_entities):
                    found_uris.add(entity_name)
                    data = dict(
                        ini=int(output['ini']),
                        fin=int(output['fin']),
                        label=output['label'],
                        url=entity_name,
                        score_list=output['score_list']
                    )
                    summary.append(data)
            # if oracle setting is on and output entities reach the number of expected entities
            if self.oracle and len(summary) >= len(expected_entities):
                break
        # Fill until get same amount as expected entities, if oracle seting is on
        if self.oracle and len(summary) < len(expected_entities):
            for _ in range(len(expected_entities) - len(summary)):
                summary.append({"ini": 0, "fin": 0, "label": 'unknown', "url": 'wd:Q0'})
        return summary


# add FullSystems to the EntityLinkingDict for the load_model method
EntityLinkingDict['FullSystem'] = FullSystems
