import numpy as np
from matplotlib import pyplot as plt
from pyvad import vad

def NR(y, sr, mode=3, plot=True):
    time = np.linspace(0, len(y) / sr, len(y))
    vact = vad(y, sr, fs_vad=8000, hop_length=10, vad_mode=mode)

    y2 = []
    for i in range(len(vact)):
        if vact[i] != 1:
            y2.append(y[i])
        else:
            y2.append(0)

    if plot:
        plt.figure()
        plt.plot(time, y, 'skyblue')
        plt.plot(time, vact, 'gold')
        plt.plot(time, y2, 'salmon')
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        # plt.savefig(f"./result/img/{filename}_VAD.png")
        # plt.close()

    try:
        # perform noise reduction
        y3 = nr.reduce_noise(audio_clip=np.array(y), noise_clip=np.array(y2), verbose=False)
        return y3
    except:
        return y