from .utils import second_to_sample, sample_to_second

import numpy as np
from itertools import groupby
from typing import List, Tuple
from collections import namedtuple
from time import time

from operator import or_
from functools import reduce
from django.db.models import Q
from main.models import Recording, Fingerprint

MatchedRecord = namedtuple('MatchedRecord', ['recording_id', 'recording_name', 'input_total_hashes',
                                             'fingerprinted_hashes_in_db', 'hashes_matched_in_input',
                                             'input_confidence', 'fingerprinted_confidence',
                                             'timestamp', 'timestamp_in_seconds', 'file_sha1'])

def find_and_align(hashes: List[Tuple[str, int]], category: str = 'default',
                   threshold_duration: int = 0, threshold_count: int = 10, topn: int = 5):
    t = time()
    matches, dedup_hashes = find_matches(hashes, category=category)
    query_time = time() - t
    print(f"Time for query: {query_time:.2f}s\n")

    topn_segment = 10
    topn_recording = topn
    sorted_matches = sorted(matches, key=lambda m: (m[0], m[1], m[2][0]))
    counts = []
    for key, group in groupby(sorted_matches, key=lambda m: (m[0], m[1])):
        group_list = list(group)
        counts.append((*key, len(group_list), group_list[0][-1], group_list[-1][-1]))

    recording_matches = sorted([sorted(list(group), key=lambda g: g[2], reverse=True) \
                                for key, group in groupby(counts, key=lambda count: count[0])][:topn_segment],
                               key=lambda c: c[0][2], reverse=True)

    recording_result = []
    if len(recording_matches) > 0:
        # recording_matches = sorted(recording_matches, key=lambda m: m[0][2], reverse=True)
        threshold_duration = second_to_sample(threshold_duration)
        for candidate in recording_matches[:topn_recording]:
            timestamp = []
            tol = second_to_sample(2)
            for rid, offset, count, onset_time, offset_time in candidate:
                if count > threshold_count and offset > 0 and offset_time[0] - onset_time[0] >= threshold_duration:
                    if not np.any([onset_time[0] in range(x-tol, y+tol) for x, y in timestamp]) and \
                            not np.any([offset_time[0] in range(x-tol, y+tol) for x, y in timestamp]):
                        timestamp.append((onset_time[0], offset_time[0]))

            if len(timestamp) > 0:
                recording = Recording.objects.filter(id=rid).first()
                # time_in_sec = []
                # for t in timestamp:
                #     time_in_sec.append({
                #         'onset': f"{sample_to_second(t[0]):.3f}",
                #         'offset': f"{sample_to_second(t[1]):.3f}",
                #     })
                time_in_sec = [tuple(map(float, map("{:.3f}".format, \
                                                    (sample_to_second(t[0]), sample_to_second(t[1]))))) for t in
                               timestamp]
                hashes_matched = dedup_hashes[rid]

                record = MatchedRecord(
                    recording_id=rid,
                    recording_name=recording.filename.split('.')[0],
                    input_total_hashes=len(hashes),
                    fingerprinted_hashes_in_db=recording.total_hashes,
                    hashes_matched_in_input=hashes_matched,
                    input_confidence=round(hashes_matched / len(hashes), 2),
                    fingerprinted_confidence=round(hashes_matched / recording.total_hashes, 2),
                    timestamp=timestamp,
                    timestamp_in_seconds=time_in_sec,
                    file_sha1=recording.file_sha1.encode('utf-8')
                )

                recording_result.append(record)
                print(f"{rid} {recording.filename} / {time_in_sec}")

    return recording_result, query_time

def find_matches(hashes: List[Tuple[str, int]], category: str):
    mapping_list = {}
    for hsh, offset in hashes:
        if hsh in mapping_list.keys():
            mapping_list[hsh].append(offset)
        else:
            mapping_list[hsh] = [offset]

    values = list(mapping_list.keys())
    dedup_hashes = {}
    results = []
    queryset = Fingerprint.objects.filter(hash__in=values, recording__category=category).all()

    for fingerprint in queryset:
        hsh = fingerprint.hash
        sid = fingerprint.recording.id
        offset = fingerprint.offset

        if sid not in dedup_hashes.keys():
            dedup_hashes[sid] = 1
        else:
            dedup_hashes[sid] += 1

        for recording_sampled_offset in mapping_list[hsh]:
            results.append((sid, offset - recording_sampled_offset, [offset, recording_sampled_offset]))

    return results, dedup_hashes
