from time import time
from typing import Dict

import main.dejavu.logic.decoder as decoder
from main.dejavu.base_classes.base_recognizer import BaseRecognizer
from main.dejavu.config.settings import (ALIGN_TIME, FINGERPRINT_TIME, QUERY_TIME,
                                    RESULTS, TOTAL_TIME)

class FileRecognizer(BaseRecognizer):
    def __init__(self):
        super().__init__()

    def recognize_file(self, filename: str) -> Dict[str, any]:
        limit = None
        channels, self.Fs, _ = decoder.read(filename, limit)

        t = time()
        matches, fingerprint_time, query_time, align_time = self._recognize(*channels)
        t = time() - t

        results = {
            TOTAL_TIME: t,
            FINGERPRINT_TIME: fingerprint_time,
            QUERY_TIME: query_time,
            ALIGN_TIME: align_time,
            RESULTS: matches
        }

        return results

    def recognize(self, filename: str) -> Dict[str, any]:
        return self.recognize_file(filename)
