import re
from pathlib import Path
from typing import Optional, List, Union, Dict, Set

import nltk
from nltk.corpus import stopwords

from dataset_tools import QuestionCase
from entity_linking.base_entitity_linking_system import EntityLinkingDict
from entity_linking.ensemble_entity_linking_system import EnsembleEntityLinkingSystem, MAX_THRESHOLD
from query_tools import WIKIDATA_ENTITY_PATTERN


class PrecisionPrioritySystem(EnsembleEntityLinkingSystem):
    """
    Class for the Precision Priority system.
    It enhance the performance in the Entity Linking task by following a priority annotation process
    for the given individual Entity Linking systems. Systems with higher precision have higher priority.
    """
    def __init__(self, system_priority: Optional[List[str]] = None, joined_results: Optional[Union[Path, str]] = None,
                 threshold: Optional[int] = None, filter_stopwords: bool = False, tiebreak: bool = True):
        """
        PrecisionPrioritySystem class constructor.

        :param system_priority: Set system name priority. By default is: Aida - OpenTapioca - TAGME - DBpedia Spotlight
        :param joined_results: offline joined results from individual Entity Linking systems.
                                If no joined results are provided, the system performs a default online setting.
        :param threshold: number of expected entities to be returned. By default is 3.
        :param filter_stopwords: if True, applies mention stopwords filtering.
        :param tiebreak: if True, applies tiebreak feature to resolves ties by using entities' scores.
        """
        super().__init__(joined_results, offline=joined_results is not None)
        self.system_priority = system_priority if system_priority else \
            ["Aida", "Open Tapioca", "TAGME", "DBpedia Spotlight"]
        self.threshold = threshold if threshold else MAX_THRESHOLD
        # Load stopwords, otherwise download first
        try:
            self._stopwords = set(stopwords.words('english'))
        except LookupError:
            nltk.download('stopwords')
            self._stopwords = set(stopwords.words('english'))
        self.filter_stopwords = filter_stopwords
        self.tiebreak = tiebreak

    def __str__(self):
        """
        Get the string representation. Usually the system name.

        :return: ComposedEntityLinkingSystem string representation.
        """
        return 'Precision Priority'

    def _valid_entity(self, entity_name: str, found_uris: Set[str], mention_label: str) -> bool:
        """
        Return True if the given entity name is valid to be added to the final output annotations.
        An entity is valid if satisfy the following conditions:
            (1) entity is a Wikidata entity
            (2) entity has not been found
            (3) the stopwords filter is on and the mention label is not a stopword

        :param entity_name: entity name string.
        :param found_uris: URIs found so far (to avoid duplicates).
        :param mention_label: mention label string.
        :return:
        """
        return re.match(WIKIDATA_ENTITY_PATTERN, entity_name) and (                         # (1)
                entity_name not in found_uris) and (                                        # (2)
                not self.filter_stopwords or mention_label.lower() not in self._stopwords)  # (3)

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
        # Set number of expected entities to be returned
        num_expected_entities = num_entities_expected if num_entities_expected else self.threshold
        # sort systems' annotations by priority, ascending
        for case in sorted(results["annotations"], key=lambda a_case: self.system_priority.index(a_case['system'])):
            # sort each annotation by entity score, descending
            for output in sorted(case['output'], key=lambda output_case: -output_case['score']):
                # compress Wikidata Entity URI
                entity_name = output['url'] if 'wd:' in output['url'] else ('wd:' + output['url'])
                # add only if entity is valid
                if self._valid_entity(entity_name, found_uris, output['label']):
                    found_uris.add(entity_name)
                    data = dict(
                        ini=int(output['ini']),
                        fin=int(output['fin']),
                        label=output['label'],
                        url=entity_name,
                        score_list=output['score_list']
                    )
                    summary.append(data)
                # if tiebreak setting is on and we reach the number of expected entities
                if self.tiebreak and len(summary) >= num_expected_entities:
                    return summary
            # if current valid annotations exceed number of expected entities
            if len(summary) >= num_expected_entities:
                break
        return summary


# add PrecisionPrioritySystem to the EntityLinkingDict for the load_model method
EntityLinkingDict['PrecisionPrioritySystem'] = PrecisionPrioritySystem
