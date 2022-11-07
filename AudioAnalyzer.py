import sounddevice as sd
import audioop
import RealTimePlayer as rtp
from math import log10
from scipy.fft import fft
import scipy
import numpy as np


def get_audio_input_list():
    audio_devices_list = []
    d = list(sd.query_devices())
    print(d)
    for i in d:
        if 'mic' in str(i).lower() and not 'microsoft' in str(i).lower():
            index = i['index']
            index = index if len(str(index)) > 1 else f'0{index}'
            name = i['name']
            audio_devices_list.append(f'{index}-{name}')
    audio_devices_list.sort()
    return audio_devices_list


def get_audio_output_list():
    audio_devices_list = []
    d = list(sd.query_devices())
    print(d)
    for i in d:
        if 'mic' not in str(i).lower() and 'microsoft' not in str(i).lower():
            index = i['index']
            index = index if len(str(index)) > 1 else f'0{index}'
            name = i['name']
            audio_devices_list.append(f'{index}-{name}')
    audio_devices_list.sort()
    return audio_devices_list


def calculate_rms(data):
    rms = audioop.rms(data[-1024:], 2) / 32767
    return rms


def calculate_db(rms):
    db = 20 * log10(rms)
    return int(db)


def calculate_audio_freq(player):
    fftData = np.abs(np.fft.rfft(player.raw_data))
    which = fftData[1:].argmax() + 1
    if which != len(fftData)-1:
        y0, y1, y2 = np.log(fftData[which-1:which+2:])
        x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
        # find the frequency and output it
        thefreq = (which+x1)*player.RATE/player.CHUNK
        return int(thefreq)
    else:
        thefreq = which*player.RATE/player.CHUNK
        return int(thefreq)

# print(sd.query_devices())
# print(get_audio_output_list())


