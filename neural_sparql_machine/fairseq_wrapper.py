from pathlib import Path
from typing import List, Optional, Union

from fairseq.models import BaseFairseqModel


class FairseqTranslator:

    def __init__(self, vocab_path: Union[Path, str], checkpoints_folder: Union[Path, str], checkpoint_file: Optional[str] = None,
            gpu: bool = False):
        self.translator = BaseFairseqModel.from_pretrained(
            str(checkpoints_folder),
            checkpoint_file=checkpoint_file if checkpoint_file else 'checkpoint_best.pt',
            data_name_or_path=str(vocab_path),
        )
        self.translator = self.translator.cuda() if gpu else self.translator
        self.gpu = gpu

    def evaluate(self, sentences: List[str]) -> List[str]:
        output_predictions = []
        for sentence in sentences:
            prediction = self.translator.translate(sentence)
            output_predictions.append(prediction)
        return output_predictions

    def evaluate_best_n(self, sentence: str, beam: int = 5, verbose: bool = False, **kwargs) -> List[str]:
        input = self.translator.encode(sentence)
        best_hypos = self.translator.generate(input, beam, verbose, **kwargs)
        return [self.translator.decode(hypo['tokens']) for hypo in best_hypos]

