import main.method.shazam_fingerprint as sf
from main.method.settings import FS, \
    MIN_DURATION_RATIO, \
    MIN_HASH_COUNT

import numpy as np
from time import time
from typing import List
from collections import namedtuple
AnalysisResult = namedtuple('AnalysisResult', ['event_name', 'category', 'extension', 'fingerprint_time', 'query_time',
                                               'matched_result', 'accuracy'], defaults={0.0})

def recognize_file(file: str, category: str, params: dict, is_stream: bool, tlim: List[int]=None):
    if tlim:
        data, fs, duration, _= sf.read(file, is_stream=is_stream, start=tlim[0], end=tlim[1])
    else:
        data, fs, duration, _ = sf.read(file, is_stream=is_stream)
    fingerprint_time = []
    hashes = set()
    for channel in data:
        t = time()
        fingerprints = sf.fingerprint(channel, fs,
                                      threshold=params['thsld'], fan_size=params['fan'])
        fingerprint_time.append(time() - t)
        hashes |= set(fingerprints)

    result, query_time = sf.find_and_align(hashes, category=category, topn=10,
                                            threshold_duration=duration * MIN_DURATION_RATIO,
                                            threshold_count=MIN_HASH_COUNT)
    results = AnalysisResult(event_name=file,
                             category=category,
                             extension='.wav',
                             fingerprint_time=np.sum(fingerprint_time),
                             query_time=query_time,
                             matched_result=result)
    return results