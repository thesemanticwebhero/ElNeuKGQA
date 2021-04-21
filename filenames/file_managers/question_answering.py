from pathlib import Path
from typing import Optional

from filenames.file_managers.query_generation import BaseQueryGenerationFiles, QueryGenerationFiles


class QuestionAnsweringFiles(BaseQueryGenerationFiles):

    def __init__(self,
                 dataset_name: str = 'lcquad2',
                 dataset_variant: str = 'standard',
                 only_train: bool = False, only_valid: bool = False, only_test: bool = False,
                 train_prefix: str = 'train',
                 valid_prefix: str = 'valid',
                 test_prefix: str = 'test',
                 base_folder: Optional[Path] = None,
                 make_dir: bool = True,
                 model_type: str = 'fconv',
                 ):
        empty_sparql = True
        super().__init__('question_answering', empty_sparql, dataset_name, dataset_variant, only_train,
                         only_valid, only_test, False, True, True, train_prefix, valid_prefix, test_prefix,
                         base_folder, make_dir=make_dir, model_type=model_type)

    def base_dataset_file(self, **kwargs):
        return super().dataset_file(**kwargs)

    def dataset_file(self, **kwargs):
        return self.data_folder / "dataset_{0}_{1}_answers.json".format(self.dataset_name, self.dataset_variant)

    def load_query_generation_file_manager(self) -> QueryGenerationFiles:
        return QueryGenerationFiles(self.dataset_name, self.dataset_variant, self.only_train, self.only_valid,
                                    self.only_test, base_folder=self.base_folder, make_dir=self.make_dir,
                                    model_type=self.model_type)
