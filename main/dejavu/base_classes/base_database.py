from typing import Dict, List, Tuple

from operator import or_
from functools import reduce
from django.db.models import Q
from main.models import \
    Fingerprint
    # FingerprintWithNR

def return_matches(hashes: List[Tuple[str, int]], category: str,
                   batch_size: int = 1000) -> Tuple[List[Tuple[int, int]], Dict[int, int]]:
    """
    Searches the database for pairs of (hash, offset) values.

    :param hashes: A sequence of tuples in the format (hash, offset)
        - hash: Part of a sha1 hash, in hexadecimal format
        - offset: Offset this hash was created from/at.
    :param batch_size: number of query's batches.
    :return: a list of (sid, offset_difference) tuples and a
    dictionary with the amount of hashes matched (not considering
    duplicated hashes) in each song.
        - song id: Song identifier
        - offset_difference: (database_offset - sampled_offset)
    """
    # Create a dictionary of hash => offset pairs for later lookups
    mapper = {}
    for hsh, offset in hashes:
        if hsh in mapper.keys():
            mapper[hsh].append(offset)
        else:
            mapper[hsh] = [offset]

    values = list(mapper.keys())

    # in order to count each hash only once per db offset we use the dic below
    dedup_hashes = {}


    results = []
    # Model = Fingerprint if category == 'origin' else FingerprintWithNR
    print(f'{category} {Model}')
    for index in range(0, len(values), batch_size):
        queryset = Fingerprint.objects.filter(reduce(or_, [Q(hash=hsh) for hsh in values[index: index + batch_size]]), \
                                        recording__category=category)

        for fingerprint in queryset:
            hsh = fingerprint.hash
            sid = fingerprint.recording.id
            offset = fingerprint.offset

            if sid not in dedup_hashes.keys():
                dedup_hashes[sid] = 1
            else:
                dedup_hashes[sid] += 1
            #  we now evaluate all offset for each  hash matched
            for song_sampled_offset in mapper[hsh]:
                results.append((sid, offset - song_sampled_offset))

    return results, dedup_hashes