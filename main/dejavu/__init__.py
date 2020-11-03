import multiprocessing
import os, sys
import traceback

import main.dejavu.logic.decoder as decoder
from main.dejavu.logic.fingerprint import fingerprint

from main.models import Recording, Fingerprint
from main.serializers import RecordingSerializer, FingerprintSerializer

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