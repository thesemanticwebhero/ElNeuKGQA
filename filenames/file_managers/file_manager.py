import os
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(os.path.dirname(__file__)).parents[1]
PROJECT_DATA_FOLDER = PROJECT_ROOT / 'data'
PROJECT_WIKIDATA_QA_DATA_FOLDER = PROJECT_DATA_FOLDER / 'datasets'
PROJECT_WIKIDATA_BENCHMARK_FOLDER = PROJECT_DATA_FOLDER / 'benchmark'
PROJECT_WIKIDATA_MODELS_FOLDER = PROJECT_DATA_FOLDER / 'models'


class FileManager():

    def __init__(self, task_name: str, dataset_name: str, dataset_variant: str,
                 only_train: bool = False, only_valid: bool = False, only_test: bool = False,
                 base_folder: Optional[Path] = None,
                 data_folder: Optional[Path] = None, benchmark_folder: Optional[Path] = None,
                 models_folder: Optional[Path] = None, make_dir: bool = True):
        assert not (int(only_train) + int(only_valid) + int(only_test)) > 1
        self.dataset_name = dataset_name
        self.dataset_variant = dataset_variant
        self.task_name = task_name
        self.only_train = only_train
        self.only_valid = only_valid
        self.only_test = only_test
        self.make_dir = make_dir
        self.base_folder = base_folder if base_folder else PROJECT_DATA_FOLDER
        self.make_dir_exists_ok(self.base_folder)
        self.data_folder = data_folder if data_folder else (self.base_folder / 'datasets')
        self.make_dir_exists_ok(self.data_folder)
        self.benchmark_folder = benchmark_folder if benchmark_folder else (self.base_folder / 'benchmark')
        self.make_dir_exists_ok(self.benchmark_folder)
        self.models_folder = models_folder if models_folder else (self.base_folder / 'models')
        self.make_dir_exists_ok(self.models_folder)
        self.benchmark_task_folder = self.benchmark_folder / self.task_name
        self.make_dir_exists_ok(self.benchmark_task_folder)

    def make_dir_exists_ok(self, path: Path):
        path.mkdir(exist_ok=True) if self.make_dir else None

    def dataset_file(self, **kwargs):
        return self.data_folder / "dataset_{0}_{1}.json".format(self.dataset_name, self.dataset_variant)

    def results_folder(self, **kwargs) -> Path:
        if self.only_train:
            folder = self.benchmark_task_folder / '{0}_{1}_train'.format(self.dataset_name, self.dataset_variant)
        elif self.only_valid:
            folder = self.benchmark_task_folder / '{0}_{1}_valid'.format(self.dataset_name, self.dataset_variant)
        elif self.only_test:
            folder = self.benchmark_task_folder / '{0}_{1}_test'.format(self.dataset_name, self.dataset_variant)
        else:
            folder = self.benchmark_task_folder / '{0}_{1}'.format(self.dataset_name, self.dataset_variant)
        self.make_dir_exists_ok(folder)
        return folder

    def output_file(self, system_name: str, **kwargs) -> Path:
        folder = self.results_folder() / system_name
        self.make_dir_exists_ok(folder)
        return folder / 'output.json'

    def stats_file(self, system_name: str, **kwargs) -> Path:
        folder = self.results_folder() / system_name
        self.make_dir_exists_ok(folder)
        return folder / 'stats.json'

    def table_file(self, system_name: str, table_name: Optional[str] = None, **kwargs) -> Path:
        folder = self.results_folder() / system_name
        self.make_dir_exists_ok(folder)
        return folder / f'{table_name if table_name else "table"}.csv'

    def resources_folder(self, **kwargs) -> Path:
        pass

    def vocab_folder(self, **kwargs) -> Path:
        pass

    def model_folder(self, **kwargs) -> Path:
        pass

    def normalized_dataset_file(self, **kwargs) -> Path:
        pass

    def train_file(self, **kwargs) -> Path:
        pass

    def valid_file(self, **kwargs) -> Path:
        pass

    def test_file(self, **kwargs) -> Path:
        pass

    def train_source_file(self, **kwargs) -> Path:
        pass

    def train_target_file(self, **kwargs) -> Path:
        pass

    def valid_source_file(self, **kwargs) -> Path:
        pass

    def valid_target_file(self, **kwargs) -> Path:
        pass

    def test_source_file(self, **kwargs) -> Path:
        pass

    def test_target_file(self, **kwargs) -> Path:
        pass
