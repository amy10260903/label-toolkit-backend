from .extract import fingerprint

from pydub import AudioSegment
from hashlib import sha1
import numpy as np

from typing import List, Tuple
from time import time
import os
from main.method.settings import \
    THRESHOLD, FAN_SIZE, \
    FS, NOVERLAP


def read(filename: str, fs: int=FS, start: float=None, end: float=None, is_stream: bool=False) \
            -> Tuple[List[List[int]], int, str]:
    if start is not None and end is not None:
        audiofile = AudioSegment.from_file(filename)[start * 1000: end * 1000]
    else:
        audiofile = AudioSegment.from_file(filename)

    audiofile = audiofile.set_frame_rate(fs)
    fs = audiofile.frame_rate

    duration = audiofile.duration_seconds
    data = np.frombuffer(audiofile.raw_data, np.int16)

    channels = []
    for chn in range(audiofile.channels):
        channels.append(data[chn::audiofile.channels])

    return channels, fs, duration, file_hashes(filename, is_stream)


def sample_to_second(nsample: int, fs: int = FS, noverlap: int = NOVERLAP) -> float:
    return round(nsample / fs * noverlap, 2)


def second_to_sample(nsecond: float, fs: int = FS, noverlap: int = NOVERLAP) -> int:
    return int(nsecond * fs / noverlap)


def file_hashes(file: str, is_stream: bool) -> str:
    file_sha1 = sha1()
    if is_stream:
        file.seek(0)
        file_sha1.update(file.read())
    else:
        with open(file, 'rb') as f:
            file_sha1.update(f.read())
    return file_sha1.hexdigest().upper()


def fingerprint_file(filepath: str, fs: int = FS, start: float = None, end: float = None,
                     threshold: int = THRESHOLD, fan_size: int = FAN_SIZE, norm: bool = False,
                     print_output: bool = False, is_stream: bool = False):
    postfix = f"_{str(start)}_{str(end)}" if start is not None and end is not None else ""
    filename = f"{os.path.basename(filepath).split('.')[0]}{postfix}"
    channels, fs, duration, file_hash = read(filepath, fs, start, end, is_stream)

    fingerprints = set()
    channel_num = len(channels)
    fingerprint_time = []
    for chn, data in enumerate(channels, start=1):
        if print_output:
            print(f"Fingerprinting channel {chn}/{channel_num} for {filename}")

        t = time()
        hashes = fingerprint(data, fs, fan_size=fan_size, threshold=threshold, norm=norm)
        fingerprint_time.append(time() - t)

        if print_output:
            print(f"Finished channel {chn}/{channel_num} for {filename}")

        fingerprints |= set(hashes)

    return fingerprints, duration, file_hash, np.sum(fingerprint_time)