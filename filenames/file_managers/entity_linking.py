from pathlib import Path
from typing import Optional
from filenames.file_managers.file_manager import FileManager

###########################################################################################
################################### ENTITY LINKING ########################################
###########################################################################################


class EntityLinkingFiles(FileManager):

    def __init__(self,
                 dataset_name: str = 'lcquad2',
                 dataset_variant: str = 'standard',
                 only_train: bool = False, only_valid: bool = False, only_test: bool = False,
                 base_folder: Optional[Path] = None,
                 benchmark_folder: Optional[Path] = None,
                 make_dir: bool = True):
        super().__init__('entity_linking', dataset_name, dataset_variant, only_train,
                         only_valid, only_test, base_folder, benchmark_folder, make_dir=make_dir)
