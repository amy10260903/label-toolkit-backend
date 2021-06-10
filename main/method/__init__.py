import multiprocessing
import traceback
from glob import glob
import os
import sys

import main.method.shazam_fingerprint as sf
from main.models import \
    Recording, \
    Fingerprint

from main.method.settings import \
    THRESHOLD, FAN_SIZE
from main.method.recognizer import recognize_file

songhashes_set = set()
def __load_fingerprinted_audio_hashes(category: str='default') -> None:
    recordings = Recording.objects.filter(category=category, fingerprinted=True)
    for audio in recordings:
        file_hash = audio.file_sha1
        songhashes_set.add(file_hash)

def fingerprint_directory(path: str, extensions: str, category: str, nprocesses: int=None) -> None:
    try:
        nprocesses = nprocesses or multiprocessing.cpu_count()
    except NotImplementedError:
        nprocesses = 1
    else:
        nprocesses = 1 if nprocesses <= 0 else nprocesses
    pool = multiprocessing.Pool(nprocesses)

    files_to_fingerprint = []
    files = glob(os.path.join(path, f"*.{extensions}"))
    __load_fingerprinted_audio_hashes(category=category)
    for f in sorted(files):
        filename = os.path.basename(f)

        if sf.file_hashes(f, is_stream=False) in songhashes_set:
            print(f"{filename} already fingerprinted, continuing...")
            continue
        files_to_fingerprint.append(f)

    worker_input = files_to_fingerprint
    iterator = pool.imap_unordered(_fingerprint_worker, worker_input)
    while True:
        try:
            filename, hashes, file_hash = next(iterator)
        except multiprocessing.TimeoutError:
            continue
        except StopIteration:
            break
        except Exception:
            print("Failed fingerprinting")
            traceback.print_exc(file=sys.stdout)
        else:
            data = {
                'filename': filename,
                'file_sha1': file_hash,
                'category': category,
                'hashes': hashes
            }
            update_recording_file(data)

    pool.close()
    pool.join()

def update_recording_file(args):
    filename = args['filename']
    category = args['category']
    file_hash = args['file_sha1']
    hashes = args['hashes']

    recording, created = Recording.objects.get_or_create(
        filename=filename,
        category=category,
        defaults={
            'file_sha1': file_hash,
            'total_hashes': len(hashes)
        }
    )

    for hsh, offset in hashes:
        Fingerprint.objects.get_or_create(
            recording=recording,
            hash=hsh,
            offset=offset,
        )

    recording.fingerprinted = True
    recording.save()
    __load_fingerprinted_audio_hashes()

def recognize(*options):
    return recognize_file(*options)

def _fingerprint_worker(args):
    try: file = args
    except ValueError: pass

    hashes, _, file_hash, _ = sf.fingerprint_file(file, print_output=True,
                                                  threshold=THRESHOLD, fan_size=FAN_SIZE)
    return os.path.basename(file), hashes, file_hash