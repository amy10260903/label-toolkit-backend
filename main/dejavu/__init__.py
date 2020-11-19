import multiprocessing
import os, sys
import traceback
from itertools import groupby
from time import time
from typing import Dict, List, Tuple

import main.dejavu.logic.decoder as decoder
from main.dejavu.logic.fingerprint import fingerprint
from main.dejavu.base_classes.base_database import return_matches

from main.models import Recording, Fingerprint
from main.serializers import RecordingSerializer, FingerprintSerializer
from main.dejavu.config.settings import (DEFAULT_FS, DEFAULT_OVERLAP_RATIO,
                                    DEFAULT_WINDOW_SIZE, FIELD_FILE_SHA1,
                                    FIELD_TOTAL_HASHES,
                                    FINGERPRINTED_CONFIDENCE,
                                    FINGERPRINTED_HASHES, HASHES_MATCHED,
                                    INPUT_CONFIDENCE, INPUT_HASHES, OFFSET,
                                    OFFSET_SECS, SONG_ID, SONG_NAME, TOPN)

songhashes_set = set()

def __load_fingerprinted_audio_hashes() -> None:
    """
    Keeps a dictionary with the hashes of the fingerprinted songs, in that way is possible to check
    whether or not an audio file was already processed.
    """
    # get songs previously indexed
    recordings = Recording.objects.all()
    for song in recordings:
        song_hash = song.file_sha1
        songhashes_set.add(song_hash)

def fingerprint_directory(path: str, extensions: str, nprocesses: int = None) -> None:
    """
    Given a directory and a set of extensions it fingerprints all files that match each extension specified.

    :param path: path to the directory.
    :param extensions: list of file extensions to consider.
    :param nprocesses: amount of processes to fingerprint the files within the directory.
    """
    # Try to use the maximum amount of processes if not given.
    try:
        nprocesses = nprocesses or multiprocessing.cpu_count()
    except NotImplementedError:
        nprocesses = 1
    else:
        nprocesses = 1 if nprocesses <= 0 else nprocesses

    pool = multiprocessing.Pool(nprocesses)

    filenames_to_fingerprint = []
    for filename, _ in decoder.find_files(path, extensions):
        # don't refingerprint already fingerprinted files
        if decoder.unique_hash(filename) in songhashes_set:
            print(f"{filename} already fingerprinted, continuing...")
            continue

        filenames_to_fingerprint.append(filename)

    # Prepare _fingerprint_worker input
    limit = None
    worker_input = list(zip(filenames_to_fingerprint, [limit] * len(filenames_to_fingerprint)))

    # Send off our tasks
    iterator = pool.imap_unordered(_fingerprint_worker, worker_input)

    # Loop till we have all of them
    while True:
        try:
            song_name, hashes, file_hash = next(iterator)
        except multiprocessing.TimeoutError:
            continue
        except StopIteration:
            break
        except Exception:
            print("Failed fingerprinting")
            # Print traceback because we can't reraise it here
            traceback.print_exc(file=sys.stdout)
        else:
            recording = Recording.objects.filter(filename=song_name).first()
            if not recording:
                data = {
                    'filename': song_name,
                    'file_sha1': file_hash,
                    'total_hashes': len(hashes)
                }
                serializer = RecordingSerializer(data=data, many=False)
                if serializer.is_valid():
                    serializer.save()

                    recording = Recording.objects.filter(filename=song_name).first()
                else:
                    raise Exception(serializer.errors)

            for hash, offset in hashes:
                fingerprint = Fingerprint.objects.filter(recording=recording.id, hash=hash, offset=offset).first()
                if not fingerprint:
                    data = {
                        'recording': recording.id,
                        'hash': hash,
                        'offset': offset
                    }
                    serializer = FingerprintSerializer(data=data, many=False)
                    if serializer.is_valid():
                        serializer.save()

                        recording.fingerprinted = True
                        recording.save()
                        __load_fingerprinted_audio_hashes()
                    else:
                        raise Exception(serializer.errors)

    pool.close()
    pool.join()

def generate_fingerprints(samples: List[int], Fs=DEFAULT_FS) -> Tuple[List[Tuple[str, int]], float]:
    f"""
    Generate the fingerprints for the given sample data (channel).

    :param samples: list of ints which represents the channel info of the given audio file.
    :param Fs: sampling rate which defaults to {DEFAULT_FS}.
    :return: a list of tuples for hash and its corresponding offset, together with the generation time.
    """
    t = time()
    hashes = fingerprint(samples, Fs=Fs)
    fingerprint_time = time() - t
    return hashes, fingerprint_time

def find_matches(hashes: List[Tuple[str, int]]) -> Tuple[List[Tuple[int, int]], Dict[str, int], float]:
    """
    Finds the corresponding matches on the fingerprinted audios for the given hashes.

    :param hashes: list of tuples for hashes and their corresponding offsets
    :return: a tuple containing the matches found against the db, a dictionary which counts the different
    hashes matched for each song (with the song id as key), and the time that the query took.

    """
    t = time()
    matches, dedup_hashes = return_matches(hashes)
    query_time = time() - t

    return matches, dedup_hashes, query_time

def align_matches(matches: List[Tuple[int, int]], dedup_hashes: Dict[str, int], queried_hashes: int,
                  topn: int = TOPN) -> List[Dict[str, any]]:
    """
    Finds hash matches that align in time with other matches and finds
    consensus about which hashes are "true" signal from the audio.

    :param matches: matches from the database
    :param dedup_hashes: dictionary containing the hashes matched without duplicates for each song
    (key is the song id).
    :param queried_hashes: amount of hashes sent for matching against the db
    :param topn: number of results being returned back.
    :return: a list of dictionaries (based on topn) with match information.
    """
    # count offset occurrences per song and keep only the maximum ones.
    sorted_matches = sorted(matches, key=lambda m: (m[0], m[1]))
    counts = [(*key, len(list(group))) for key, group in groupby(sorted_matches, key=lambda m: (m[0], m[1]))]
    songs_matches = sorted(
        [max(list(group), key=lambda g: g[2]) for key, group in groupby(counts, key=lambda count: count[0])],
        key=lambda count: count[2], reverse=True
    )

    songs_result = []
    for song_id, offset, _ in songs_matches[0:topn]:  # consider topn elements in the result
        song = Recording.objects.filter(id=song_id).first()
        song_name = song.filename
        song_hashes = song.total_hashes
        song_file_sha1 = song.file_sha1
        nseconds = round(float(offset) / DEFAULT_FS * DEFAULT_WINDOW_SIZE * DEFAULT_OVERLAP_RATIO, 5)
        hashes_matched = dedup_hashes[song_id]

        song = {
            SONG_ID: song_id,
            SONG_NAME: song_name.encode("utf8"),
            INPUT_HASHES: queried_hashes,
            FINGERPRINTED_HASHES: song_hashes,
            HASHES_MATCHED: hashes_matched,
            # Percentage regarding hashes matched vs hashes from the input.
            INPUT_CONFIDENCE: round(hashes_matched / queried_hashes, 2),
            # Percentage regarding hashes matched vs hashes fingerprinted in the db.
            FINGERPRINTED_CONFIDENCE: round(hashes_matched / song_hashes, 2),
            OFFSET: offset,
            OFFSET_SECS: nseconds,
            FIELD_FILE_SHA1: song_file_sha1.encode("utf8")
        }

        songs_result.append(song)

    return songs_result

def recognize(recognizer, *options, **kwoptions) -> Dict[str, any]:
    r = recognizer()
    return r.recognize(*options, **kwoptions)

def _fingerprint_worker(arguments):
    # Pool.imap sends arguments as tuples so we have to unpack
    # them ourself.
    try:
        file_name, limit = arguments
    except ValueError:
        pass

    song_name, extension = os.path.splitext(os.path.basename(file_name))

    fingerprints, file_hash = get_file_fingerprints(file_name, limit, print_output=True)

    return song_name, fingerprints, file_hash

def get_file_fingerprints(file_name: str, limit: int, print_output: bool = False):
    channels, fs, file_hash = decoder.read(file_name, limit)
    fingerprints = set()
    channel_amount = len(channels)
    for channeln, channel in enumerate(channels, start=1):
        if print_output:
            print(f"Fingerprinting channel {channeln}/{channel_amount} for {file_name}")

        hashes = fingerprint(channel, Fs=fs)

        if print_output:
            print(f"Finished channel {channeln}/{channel_amount} for {file_name}")

        fingerprints |= set(hashes)

    return fingerprints, file_hash