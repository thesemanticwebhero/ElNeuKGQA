import json
import re
from pathlib import Path
from typing import List, Dict, Optional

from flair.data import Sentence
from flair.models import SequenceTagger

from dataset_tools import QuestionCase, Normalizer
from filenames.file_managers.slot_filling import SlotFillingFiles


class SlotFillerMethodNotImplemented(Exception):
    pass


SlotFillingDict = dict()


class BaseSlotFiller:

    def __str__(self):
        raise SlotFillerMethodNotImplemented

    def evaluate(self, question_case: QuestionCase) -> List[Dict]:
        raise SlotFillerMethodNotImplemented

    def evaluate_batch(self, question_cases: List[QuestionCase]) -> List[List[Dict]]:
        raise SlotFillerMethodNotImplemented

    def _normalize_batch(self, question_cases: List[QuestionCase]) -> List[str]:
        return list(Normalizer.normalize_question(case.question_text) for case in question_cases)

    @staticmethod
    def get_slot_list(question: str, slot_sequence: str) -> List[Dict]:
        results = list()
        s_question = question.lower().split()
        s_slot = slot_sequence.split()
        if len(s_slot) > len(s_question):
            s_slot = s_slot[:len(s_question)]
        in_slot = False
        slot_label = ''
        slot_placeholder = None
        for idx, slot in enumerate(s_slot + ['X']):
            if re.match('B-.*', slot):
                in_slot = True
                slot_label = s_question[idx]
                slot_placeholder = f"<{re.match('B-(.*)', slot).group(1)}>"
            elif re.match('I-.*', slot) and in_slot:
                slot_label += ' ' + s_question[idx]
            elif in_slot:
                # results[slot_label] = slot_placeholder
                results.append(dict(label=slot_label, slot=slot_placeholder))
                in_slot = False
                slot_label = ''
                slot_placeholder = None
        return results

    @classmethod
    def load_model(cls, slot_filler_opt: Dict, dataset_opt: Optional[Dict] = None) -> 'BaseSlotFiller':
        system_name = slot_filler_opt["system_name"]
        if slot_filler_opt['offline']:
            file_manager = SlotFillingFiles(**dataset_opt['params'])
            offline_results = file_manager.output_file(system_name)
            print(f'Using offline data from "{offline_results}"...')
            slot_filler = OfflineSlotFiller(system_name, offline_results)
        else:
            system_type = slot_filler_opt["system_type"]
            slot_filler = SlotFillingDict[system_type].load_model(slot_filler_opt)
        print(f"{system_name} system ready...")
        return slot_filler


class FlairNerSlotFiller(BaseSlotFiller):

    def __init__(self, model_folder: Path, model_name: Optional[str] = None, gpu: bool = False):
        self.model_folder = model_folder
        self.model_name = model_name if model_name else 'best-model.pt'
        self.model = SequenceTagger.load(self.model_folder / self.model_name)
        self.model = self.model.cuda() if gpu else self.model_name

    def __str__(self):
        return 'Flair'

    def evaluate(self, question_case: QuestionCase) -> List[Dict]:
        return self.evaluate_batch([question_case])[0]

    def evaluate_batch(self, question_cases: List[QuestionCase]) -> List[List[Dict]]:
        normalized_questions = list(Sentence(question) for question in self._normalize_batch(question_cases))
        self.model.predict(normalized_questions)
        results = []
        for sentence in normalized_questions:
            slot_list = list()
            for span in sentence.get_spans('ner'):
                span_dict = span.to_dict()
                span_slot_dict = dict()
                span_slot_dict['label'] = span_dict['text']
                span_slot_dict['slot'] = f"<{span_dict['labels'][0].value}>"
                slot_list.append(span_slot_dict)
            results.append(slot_list)
        return results

    @classmethod
    def load_model(cls, slot_filler_opt: Dict, dataset_opt: Optional[Dict] = None) -> 'FlairNerSlotFiller':
        file_manager = SlotFillingFiles(**slot_filler_opt['system_params'])
        filler_params = dict(
            model_folder=file_manager.model_folder(),
            model_name=slot_filler_opt['model_name'] if 'model_name' in slot_filler_opt else None,
            gpu=slot_filler_opt['gpu'] if 'gpu' in slot_filler_opt else False
        )
        slot_filler = FlairNerSlotFiller(**filler_params)
        return slot_filler


class OfflineSlotFiller(BaseSlotFiller):

    def __init__(self, system_name: str, offline_results: Path):
        self.system_name = system_name
        self.offline_results = offline_results
        with open(offline_results, encoding='utf-8') as inJsonFile:
            data = json.load(inJsonFile)
            self.uid_data_map = {case['uid']: case for case in data['questions']}

    def __str__(self):
        return self.system_name

    def evaluate(self, question_case: QuestionCase) -> List[Dict]:
        question_id = question_case.question_id
        if question_id not in self.uid_data_map:
            return list()
        result_case = self.uid_data_map[question_id]
        return result_case['system_slots']

    def evaluate_batch(self, question_cases: List[QuestionCase]) -> List[List[Dict]]:
        return list(self.evaluate(case) for case in question_cases)


SlotFillingDict['Flair'] = FlairNerSlotFiller
