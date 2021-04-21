from pathlib import Path
from typing import Optional

from filenames.file_managers.query_generation import BaseQueryGenerationFiles


class QueryTemplateGenerationFiles(BaseQueryGenerationFiles):

    def __init__(self, dataset_name: str = 'lcquad2',
                 dataset_variant: str = 'standard',
                 only_train: bool = False, only_valid: bool = False, only_test: bool = False,
                 query_split: bool = False, property_guarantee: bool = True, simplified: bool = True,
                 train_prefix: str = 'train', valid_prefix: str = 'valid', test_prefix: str = 'test',
                 base_folder: Optional[Path] = None, models_folder: Optional[Path] = None, make_dir: bool = True,
                 model_type: str = 'fconv',):
        empty_sparql = True
        super().__init__("query_template_generation", empty_sparql, dataset_name, dataset_variant, only_train,
                         only_valid, only_test, query_split, property_guarantee, simplified,
                         train_prefix, valid_prefix, test_prefix, base_folder, models_folder=models_folder,
                         make_dir=make_dir, model_type=model_type)


# Empty SPARQL, standard size
empty_file_standard_manager = QueryTemplateGenerationFiles(model_type='fconv')
LCQUAD2_VOCAB = empty_file_standard_manager.vocab_folder()
LCQUAD2_CONVS2S_MODEL = empty_file_standard_manager.model_folder()

# Empty SPARQL, plus size
empty_file_plus_manager = QueryTemplateGenerationFiles(dataset_variant='plus', model_type='fconv')
LCQUAD2_PLUS_VOCAB = empty_file_plus_manager.vocab_folder()
LCQUAD2_PLUS_CONVS2S_MODEL = empty_file_plus_manager.model_folder()