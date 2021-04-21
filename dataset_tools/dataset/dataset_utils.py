import json
from pathlib import Path

from typing import Optional, List, Iterable

from dataset_tools.dataset_case import NormalizedCase


class QuestionAnsweringDataIterator:

    def __init__(self, dataset_input: Path):
        """
        Constructor to iterate a normalized dataset for Question Answering.

        :param dataset_input: input dataset's string filename.
        """
        self.dataset_input = dataset_input
        with dataset_input.open(encoding='utf-8') as inJsonFile:
            print(f'Loading dataset at "{dataset_input}"...')
            self.data = json.load(inJsonFile)

    def __iter__(self) -> Iterable[NormalizedCase]:
        """
        Return a iterator with the question of the dataset.

        :return: dataset's iterator.
        """
        for case in self.data['questions']:
            yield NormalizedCase(case)

    def __len__(self):
        """
        Return dataset length, i.e. number of questions

        :return: number of questions in the dataset
        """
        return len(self.data['questions'])

    @property
    def train_cases(self) -> Optional[List[int]]:
        """
        Return list with the train cases of the dataset, if exists.

        :return: return list of train id cases, None if there are no test cases
        """
        return self.data['train'] if 'train' in self.data else None

    @property
    def valid_cases(self) -> Optional[List[int]]:
        """
        Return list with the valid cases of the dataset, if exists.

        :return: return list of valid id cases, None if there are no test cases
        """
        return self.data['valid'] if 'valid' in self.data else None

    @property
    def test_cases(self) -> Optional[List[int]]:
        """
        Return list with the test cases of the dataset, if exists.

        :return: return list of test id cases, None if there are no test cases
        """
        return self.data['test'] if 'test' in self.data else None


    @property
    def train_normalized_cases(self) -> Iterable[NormalizedCase]:
        """
        Return list with the train cases of the dataset, if exists.

        :return: return list of train id cases, None if there are no test cases
        """
        if 'train' not in self.data:
            return None
        for case in self.data['questions']:
            if case['question_id'] in self.data['train']:
                yield NormalizedCase(case)

    @property
    def valid_normalized_cases(self) -> Iterable[NormalizedCase]:
        """
        Return list with the valid cases of the dataset, if exists.

        :return: return list of valid id cases, None if there are no test cases
        """
        if 'valid' not in self.data:
            return None
        for case in self.data['questions']:
            if case['question_id'] in self.data['valid']:
                yield NormalizedCase(case)


    @property
    def test_normalized_cases(self) -> Iterable[NormalizedCase]:
        """
        Return list with the test cases of the dataset, if exists.

        :return: return list of test id cases, None if there are no test cases
        """
        if 'test' not in self.data:
            return None
        for case in self.data['questions']:
            if case['question_id'] in self.data['test']:
                yield NormalizedCase(case)


SOS_token = 0
EOS_token = 1


class Lang:
    def __init__(self, name: str, padding: bool = False):
        self.name = name
        self.word2index = {}
        self.word2count = {}
        self.padding = padding
        self.index2word = {SOS_token + int(padding): "SOS", EOS_token + int(padding): "EOS"}
        self.n_words = 2 + int(padding)  # Count SOS and EOS, leave a blank index for padding

    def addSentence(self, sentence):
        for word in sentence.split(' '):
            self.addWord(word)

    def addWord(self, word):
        if word not in self.word2index:
            self.word2index[word] = self.n_words
            self.word2count[word] = 1
            self.index2word[self.n_words] = word
            self.n_words += 1
        else:
            self.word2count[word] += 1

