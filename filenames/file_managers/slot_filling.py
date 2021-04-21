import os
from pathlib import Path
from typing import Optional

from filenames.file_managers.file_manager import FileManager

PROJECT_ROOT = Path(os.path.dirname(__file__)).parents[1]
PROJECT_DATA_FOLDER = PROJECT_ROOT / 'data'
PROJECT_WIKIDATA_QA_DATA_FOLDER = PROJECT_ROOT / 'wikidataQA_dataset'
PROJECT_WIKIDATA_BENCHMARK_FOLDER = PROJECT_ROOT / 'data' / 'benchmark'


class SlotFillingFiles(FileManager):
    def __init__(self,
                 dataset_name: str = 'lcquad2',
                 dataset_variant: str = 'standard',
                 only_train: bool = False, only_valid: bool = False, only_test: bool = False,
                 train_prefix: str = 'train',
                 valid_prefix: str = 'valid',
                 test_prefix: str = 'test',
                 base_folder: Optional[Path] = None,
                 models_folder: Optional[Path] = None, make_dir: bool = True
                 ):
        super().__init__('slot_filling', dataset_name, dataset_variant, only_train,
                         only_valid, only_test, base_folder, models_folder=models_folder, make_dir=make_dir)
        self.train_prefix = train_prefix
        self.valid_prefix = valid_prefix
        self.test_prefix = test_prefix

    def resources_folder(self, **kwargs) -> Path:
        folder = self.models_folder / 'slot_filling_{0}_{1}'.format(self.dataset_name, self.dataset_variant)
        self.make_dir_exists_ok(folder)
        return folder

    def model_folder(self, **kwargs) -> Path:
        folder = self.resources_folder() / 'flair'
        self.make_dir_exists_ok(folder)
        return folder

    def dataset_file(self, **kwargs):
        return self.data_folder / "dataset_{0}_{1}.json".format(self.dataset_name, self.dataset_variant)

    def _split_file(self, base_prefix: str):
        return self.resources_folder() / "slot_filling_{0}_{1}.txt".format(base_prefix, self.dataset_name)

    def train_file(self, **kwargs):
        return self._split_file(self.train_prefix)

    def valid_file(self, **kwargs):
        return self._split_file(self.valid_prefix)

    def _side_split_file(self, base_prefix: str, file_suffix: str):
        return self.resources_folder() / "{0}.{1}".format(base_prefix, file_suffix)

    def train_source_file(self, **kwargs) -> Path:
        return self._side_split_file(self.train_prefix, 'en')

    def train_target_file(self, **kwargs) -> Path:
        return self._side_split_file(self.train_prefix, 'seq')

    def valid_source_file(self, **kwargs) -> Path:
        return self._side_split_file(self.valid_prefix, 'en')

    def valid_target_file(self, **kwargs) -> Path:
        return self._side_split_file(self.valid_prefix, 'seq')

