import re
from collections import Counter
from pathlib import Path
from typing import Optional, List, Union, Tuple, Dict

import nltk
from nltk.corpus import stopwords

from dataset_tools import QuestionCase
from entity_linking.base_entitity_linking_system import EntityLinkingDict
from entity_linking.ensemble_entity_linking_system import EnsembleEntityLinkingSystem, MAX_THRESHOLD
from query_tools import WIKIDATA_ENTITY_PATTERN


class VotingSystem(EnsembleEntityLinkingSystem):
    """
    Class for the Voting Composed Entity Linking system.
    It enhance the performance in the Entity Linking task by implementing a voting scheme
    where each individual system cast votes on their output annotations.
    For vote ties, systems with higher priority (by default higher precision) have preference.
    """
    def __init__(self, system_priority: Optional[List[str]] = None, joined_results: Optional[Union[Path, str]] = None,
                 threshold: Optional[int] = None, filter_stopwords: bool = False, tiebreak: bool = True):
        """
        VotingSystem class constructor.

        :param system_priority: Set system name priority. By default is: Aida - OpenTapioca - TAGME - DBpedia Spotlight
        :param joined_results: offline joined results from individual Entity Linking systems.
                                If no joined results are provided, the system performs a default online setting.
        :param threshold: number of expected entities to be returned. By default is 3.
        :param filter_stopwords: if True, applies mention stopwords filtering.
        :param tiebreak: if True, applies tiebreak feature to resolves ties by using entities' scores.
        """
        super().__init__(joined_results=joined_results, offline=joined_results is not None)
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
        return 'Voting System'

    def get_priority_and_score(self, entity_output_pair: Tuple[str, Tuple[str, Dict]]) -> Tuple[int, float]:
        """
        Get system priority and entity score

        :param entity_output_pair: entity - output annotation tuple
        :return: tuple with system priority index and entity float score
        """
        system_name = entity_output_pair[1][0]
        entity_score = entity_output_pair[1][1]['score']
        return self.system_priority.index(system_name), -entity_score

    def __gather_votes(self, results_annotations: List[Dict]) -> Tuple[Counter, Dict]:
        """

        :param results_annotations:
        :return:
        """
        entity_votes = Counter()
        entity_outputs_map = dict()
        # Collect votes
        for case in results_annotations:
            for output in sorted(case['output'], key=lambda c_output: -c_output['score'] if 'score' in c_output else 0):
                entity_name = output['url'] if 'wd:' in output['url'] else ('wd:' + output['url'])
                # if entity is a Wikidata entity
                if re.match(WIKIDATA_ENTITY_PATTERN, entity_name):
                    entity_votes[entity_name] += 1
                    # if score is not provided, build one based on the Wikidata identifier, or just the entity name
                    if 'score' not in output:  # TODO: why is this here as well? (look at gather_results method)
                        output['score'] = int(re.match(r'Q(\d+)', entity_name).group(1)) \
                            if re.match(r'Q(\d+)', entity_name) else entity_name
                    # set entity_name = [..., (system_name, output_annotation), ...]
                    entity_outputs_map.setdefault(entity_name, list()).append((case['system'], output))
        # for key, value in sorted(entity_votes.items(), key=lambda p: -p[1]):
        #     print(f'{key}: {value}')
        return entity_votes, entity_outputs_map

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
        # gather entity votes, register a entity_name -> output annotations map
        entity_votes, entity_outputs_map = self.__gather_votes(results["annotations"])
        # Get max number of votes, 0 if there are no results
        max_votes = max(entity_votes.values()) if entity_votes else 0
        # adapt annotations results to the desired output
        summary = list()
        found_uris = set()
        # Set number of expected entities to be returned
        num_expected_entities = num_entities_expected if num_entities_expected else self.threshold
        # Keep most n voted entities
        for num_votes in reversed(range(1, max_votes+1)):
            # Get all entities with num_votes votes
            voted_entities = list(entity for entity, votes in entity_votes.items() if votes == num_votes)
            # Get all systems output annotations related to those entities
            voted_entity_outputs = list()
            for entity, system_output_pair in entity_outputs_map.items():
                if entity in voted_entities:
                    for pair in system_output_pair:
                        voted_entity_outputs.append((entity, pair))
            # Adding entities by prioritizing higher precision systems and better scores
            # Note that p[0] = entity_name, p[1][0] = system_name, p[1][1] = output_case
            prev_system = ''
            for entity_name, system_output in sorted(voted_entity_outputs,
                                                     key=lambda a_pair: self.get_priority_and_score(a_pair)):
                system, output = system_output
                # if (1) reached number of expected entities, and
                #    (2) tiebreak is set on or current entities does not come from the previous system
                if len(summary) >= num_expected_entities and (self.tiebreak or prev_system != system):
                    return summary
                prev_system = system
                # (1) entity has not been found, and (2) the stopwords filter is on and the mention label is not a stopword
                if entity_name not in found_uris and (not self.filter_stopwords or output['label'].lower() not in self._stopwords):
                    found_uris.add(entity_name)
                    # data = dict(output)
                    data = dict(
                        ini=int(output['ini']),
                        fin=int(output['fin']),
                        label=output['label'],
                        url=entity_name,
                        score_list=output['score_list']
                    )
                    summary.append(data)
        return summary


# add VotingSystem to the EntityLinkingDict for the load_model method
EntityLinkingDict['VotingSystem'] = VotingSystem
