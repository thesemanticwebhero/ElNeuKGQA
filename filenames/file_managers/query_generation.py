from pathlib import Path
from typing import Optional

from filenames.file_managers import FileManager


class BaseQueryGenerationFiles(FileManager):

    def __init__(self,
                 task_name: str,
                 empty_sparql: bool = True,
                 dataset_name: str = 'lcquad2',
                 dataset_variant: str = 'standard',
                 only_train: bool = False, only_valid: bool = False, only_test: bool = False,
                 query_split: bool = False,
                 property_guarantee: bool = True,
                 simplified: bool = True,
                 train_prefix: str = 'train',
                 valid_prefix: str = 'valid',
                 test_prefix: str = 'test',
                 base_folder: Optional[Path] = None,
                 data_folder: Optional[Path] = None,
                 benchmark_folder: Optional[Path] = None,
                 models_folder: Optional[Path] = None,
                 make_dir: bool = True,
                 model_type: str = 'fconv',
                 ):
        super().__init__(task_name, dataset_name, dataset_variant, only_train, only_valid, only_test, base_folder,
                         data_folder, benchmark_folder, models_folder, make_dir)
        self.dataset_type = 'empty' if empty_sparql else 'full'
        self.split_type = 'query' if query_split else 'question'
        self.guarantee = "with" if property_guarantee else "without"
        self.train_prefix = train_prefix
        self.valid_prefix = valid_prefix
        self.test_prefix = test_prefix
        self.target_suffix = "empsparql" if empty_sparql else "sparql"
        self.simplified = simplified
        self.model_type = model_type

    def resources_folder(self, **kwargs) -> Path:
        if self.simplified:
            folder = self.models_folder / "{0}_{1}_{2}".format(self.dataset_type, self.dataset_name, self.dataset_variant)
        else:
            folder = self.models_folder / "{0}_{1}_{2}_by_{3}_split_{4}_guarantee".format(self.dataset_type,
                                                                                        self.dataset_name,
                                                                                        self.dataset_variant,
                                                                                        self.split_type, self.guarantee)
        self.make_dir_exists_ok(folder)
        return folder

    def vocab_folder(self, **kwargs):
        folder = self.resources_folder() / "data-bin_{0}.tokenized.en-{1}".format(self.dataset_name, self.target_suffix)
        self.make_dir_exists_ok(folder)
        return folder

    def model_folder(self, **kwargs):
        folder = self.resources_folder() / "checkpoints_{2}_{0}_en_{1}".format(self.dataset_name, self.target_suffix,
                                                                               self.model_type)
        self.make_dir_exists_ok(folder)
        return folder

    def _split_file(self, base_prefix: str):
        return self.resources_folder() / "{0}_{1}_{2}_sparql.txt".format(base_prefix, self.dataset_name,
                                                                         self.dataset_type)

    def train_file(self, **kwargs):
        return self._split_file(self.train_prefix)

    def valid_file(self, **kwargs):
        return self._split_file(self.valid_prefix)

    def _side_split_file(self, base_prefix: str, file_suffix: str):
        return self.resources_folder() / "{0}.{1}".format(base_prefix, file_suffix)

    def train_source_file(self, **kwargs) -> Path:
        return self._side_split_file(self.train_prefix, 'en')

    def train_target_file(self, **kwargs) -> Path:
        return self._side_split_file(self.train_prefix, self.target_suffix)

    def valid_source_file(self, **kwargs) -> Path:
        return self._side_split_file(self.valid_prefix, 'en')

    def valid_target_file(self, **kwargs) -> Path:
        return self._side_split_file(self.valid_prefix, self.target_suffix)


class QueryGenerationFiles(BaseQueryGenerationFiles):

    def __init__(self, dataset_name: str = 'lcquad2',
                 dataset_variant: str = 'standard',
                 only_train: bool = False, only_valid: bool = False, only_test: bool = False,
                 query_split: bool = False, property_guarantee: bool = True, simplified: bool = True,
                 train_prefix: str = 'train', valid_prefix: str = 'valid', test_prefix: str = 'test',
                 base_folder: Optional[Path] = None, models_folder: Optional[Path] = None, make_dir: bool = True,
                 model_type: str = 'fconv',
                 ):
        empty_sparql = False
        super().__init__("query_generation", empty_sparql, dataset_name, dataset_variant, only_train, only_valid,
                         only_test, query_split, property_guarantee, simplified, train_prefix, valid_prefix, test_prefix,
                         base_folder, models_folder=models_folder, make_dir=make_dir, model_type=model_type)


# Full SPARQL, standard size
full_file_standard_manager = QueryGenerationFiles(model_type='fconv')
LCQUAD2_FULL_VOCAB = full_file_standard_manager.vocab_folder()
LCQUAD2_FULL_CONVS2S_MODEL = full_file_standard_manager.model_folder()

# Full SPARQL, plus size
full_file_plus_manager = QueryGenerationFiles(dataset_variant='plus', model_type='fconv')
LCQUAD2_FULL_PLUS_VOCAB = full_file_plus_manager.vocab_folder()
LCQUAD2_FULL_PLUS_CONVS2S_MODEL = full_file_plus_manager.model_folder()

# Baseline: Full SPARQL, standard size
LCQUAD2_BASELINE_VOCAB = LCQUAD2_FULL_VOCAB
LCQUAD2_BASELINE_CONVS2S_MODEL = LCQUAD2_FULL_CONVS2S_MODEL
