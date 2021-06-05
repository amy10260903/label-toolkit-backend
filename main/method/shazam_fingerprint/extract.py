import matplotlib.mlab as mlab
from matplotlib import pyplot as plt
import matplotlib.patches as patches
import librosa.display
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage import generate_binary_structure, \
    binary_erosion, \
    iterate_structure
from operator import itemgetter
import numpy as np
import hashlib

from typing import List, Tuple
import os

from main.method.settings import NFFT, NOVERLAP, \
    CONNECTIVITY, PEAK_NEIGHBORHOOD_SIZE, \
    FAN_SIZE, \
    MIN_FREQ_SPAN, MAX_FREQ_SPAN, \
    MIN_TIME_SPAN, MAX_TIME_SPAN

def fingerprint(data: List[int],
                fs: int,
                nfft: int = NFFT,
                noverlap: int = NOVERLAP,
                fan_size: int = 10,
                threshold: int = 10,
                norm: bool = False) -> List[Tuple[str, int]]:
    arr2D = convert_to_spectrogram(data, fs, nfft=nfft, noverlap=noverlap, convert2db=True)
    # arr2D = convert_to_spectrogram(data, fs, nfft=nfft, noverlap=noverlap)
    # arr2D = 10 * np.log10(arr2D, out=np.zeros_like(arr2D), where=(arr2D != 0))

    peaks = find_2D_peaks(arr2D, threshold=threshold, norm=norm)
    return generate_hashes(peaks, fan_size=fan_size)


def convert_to_spectrogram(data: List[int], fs: int, nfft: int = NFFT, noverlap: int = NOVERLAP,
                           convert2db: bool = False, plot: bool = False) -> np.array:
    spectrogram = mlab.specgram(
        data,
        NFFT=nfft,
        Fs=fs,
        window=mlab.window_hanning,
        noverlap=noverlap)[0]

    if convert2db:
        spectrogram = librosa.power_to_db(spectrogram, ref=np.max)

    return spectrogram


def find_2D_peaks(image: np.array, threshold: float, norm: bool, print_output: bool = False) \
        -> List[Tuple[List[int], List[int]]]:
    if norm:
        image = (image - np.min(image)) / (np.max(image) - np.min(image))
        threshold = -threshold

    struct = generate_binary_structure(2, CONNECTIVITY)
    neighborhood = iterate_structure(struct, PEAK_NEIGHBORHOOD_SIZE)
    local_max = maximum_filter(image, footprint=neighborhood) == image
    background = (image == np.min(image))
    # background = (image==0)
    eroded_background = binary_erosion(background, structure=neighborhood, border_value=1)
    detected_peaks = local_max != eroded_background

    amps = image[detected_peaks]
    #     threshold_amp = np.mean(image)*(1-threshold)
    threshold_amp = np.mean(image) + threshold
    if print_output:
        print(f'{np.max(image):.2f} dB {np.min(image):.2f} dB {np.mean(image):.2f} dB {threshold_amp:.2f} dB')
    filter_idxs = np.where(amps > threshold_amp)

    freqs, times = np.where(detected_peaks)
    freqs_filter = freqs[filter_idxs]
    times_filter = times[filter_idxs]

    return list(zip(freqs_filter, times_filter))


def generate_hashes(peaks: List[Tuple[int, int]], fan_size: int,
                    plot: bool = False, image: np.array = None) -> List[Tuple[str, int]]:
    peaks.sort(key=itemgetter(1))
    idx_freq = 0
    idx_time = 1

    hashes = []
    for i in range(len(peaks)):
        freq1, t1 = peaks[i]
        freq_min = MIN_FREQ_SPAN
        freq_max = MAX_FREQ_SPAN
        if freq1 + freq_min <= 0:
            freq_max = freq_max - (freq1 + freq_min)
        idx = i + 1
        hash_cnt = 0
        peaks_filter = []
        while (hash_cnt < fan_size and idx < len(peaks)):
            if freq1 + freq_min < peaks[idx][idx_freq] < freq1 + freq_max:
                freq2, t2 = peaks[idx]
                t_delta = t2 - t1

                if MIN_TIME_SPAN <= t_delta <= MAX_TIME_SPAN:
                    hash_cnt += 1
                    h = hashlib.sha1(f"{str(freq1)}|{str(freq2)}|{str(t_delta)}".encode('utf-8'))
                    hashes.append((h.hexdigest()[0:20], t1))
                    peaks_filter.append(peaks[idx])

            idx += 1
    return hashes