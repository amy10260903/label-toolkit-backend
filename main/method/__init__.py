from glob import glob
import os

import main.method.shazam_fingerprint as sf
from main.models import \
    Recording, \
    Fingerprint
from main.serializers import \
    RecordingSerializer, \
    FingerprintSerializer

from main.method.settings import \
    THRESHOLD, FAN_SIZE
from main.method.recognizer import recognize_file

songhashes_set = set()
def __load_fingerprinted_audio_hashes(category: str = 'default') -> None:
    recordings = Recording.objects.filter(category=category, fingerprinted=True)
    for audio in recordings:
        file_hash = audio.file_sha1
        songhashes_set.add(file_hash)

def fingerprint_directory(path: str, extensions: str, category: str) -> None:
    files = glob(os.path.join(path, f"*.{extensions}"))
    __load_fingerprinted_audio_hashes(category=category)
    print(songhashes_set)
    for f in sorted(files):
        filename = os.path.basename(f)

        if sf.file_hashes(f) in songhashes_set:
            print(f"{filename} already fingerprinted, continuing...")
            continue

        hashes, _, file_hash, _ = sf.fingerprint_file(f, print_output=True,
                                                      threshold=THRESHOLD, fan_size=FAN_SIZE)
        data = {
            'filename': filename,
            'file_sha1': file_hash,
            'category': category,
            'hashes': hashes
        }
        update_recording_file(data)

def update_recording_file(args):
    filename = args['filename']
    category = args['category']
    file_hash = args['file_sha1']
    hashes = args['hashes']

    recording = Recording.objects.filter(filename=filename, category=category).first()
    if not recording:
        data = {
            'category': category,
            'filename': filename,
            'file_sha1': file_hash,
            'total_hashes': len(hashes)
        }
        serializer = RecordingSerializer(data=data, many=False)
        if serializer.is_valid():
            serializer.save()

            recording = Recording.objects.filter(category=category, filename=song_name).first()
        else:
            raise Exception(serializer.errors)

    for hsh, offset in hashes:
        fingerprint = Fingerprint.objects.filter(recording=recording.id, hash=hsh, offset=offset).first()
        if not fingerprint:
            data = {
                'recording': recording.id,
                'hash': hsh,
                'offset': offset
            }
            serializer = FingerprintSerializer(data=data, many=False)
            if serializer.is_valid():
                serializer.save()

                recording.fingerprinted = True
                recording.save()
            else:
                raise Exception(serializer.errors)

    __load_fingerprinted_audio_hashes()

def recognize(*options):
    # tlim = [89.5, 116]
    # return recognize_file(*options, tlim)
    return recognize_file(*options)