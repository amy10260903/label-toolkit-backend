import abc
from time import time
from typing import Dict, List, Tuple

import numpy as np

from main.dejavu.config.settings import DEFAULT_FS
from main.dejavu import generate_fingerprints, find_matches, align_matches


class BaseRecognizer(object, metaclass=abc.ABCMeta):
    def __init__(self):
        self.Fs = DEFAULT_FS

    def _recognize(self, *data, category) -> Tuple[List[Dict[str, any]], int, int, int]:
        fingerprint_times = []
        hashes = set()  # to remove possible duplicated fingerprints we built a set.
        for channel in data:
            fingerprints, fingerprint_time = generate_fingerprints(channel, Fs=self.Fs)
            fingerprint_times.append(fingerprint_time)
            hashes |= set(fingerprints)

        matches, dedup_hashes, query_time = find_matches(hashes, category)

        t = time()
        final_results = align_matches(matches, dedup_hashes, len(hashes), category)
        align_time = time() - t

        return final_results, np.sum(fingerprint_times), query_time, align_time

    @abc.abstractmethod
    def recognize(self) -> Dict[str, any]:
        pass  # base class does nothing
