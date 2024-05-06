import numpy as np
import pyaudio
import soundfile as sf
from scipy.spatial.distance import cosine

rms = None
db = None
freq = None
audio_status = False
similarity = -10

def get_audio_input_list():
    audio_devices_list = []
    p = pyaudio.PyAudio()
    devices = p.get_device_count()
    for i in range(devices):
        # Get the device info
        device_info = p.get_device_info_by_index(i)
        # Check if this device is a microphone (an input device)
        if device_info.get('maxInputChannels') > 0:
            audio_devices_list.append(f'{device_info.get("index")}-{device_info.get("name")}')
    return audio_devices_list


def get_audio_output_list():
    audio_devices_list = []
    p = pyaudio.PyAudio()
    devices = p.get_device_count()
    for i in range(devices):
        # Get the device info
        device_info = p.get_device_info_by_index(i)
        # Check if this device is a microphone (an input device)
        if device_info.get('maxInputChannels') == 0:
            audio_devices_list.append(f'{device_info.get("index")}-{device_info.get("name")}')
    return audio_devices_list


def calculate_audio_freq(player):
    fftData = np.abs(np.fft.rfft(player.data))
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


def get_audio_state():
    global audio_status
    if audio_status:
        j = {"id": 1, "jsonrpc": "2.0", "result": "audio"}
    else:
        j = {"id": 1, "jsonrpc": "2.0", "result": "mute"}
    return j


def get_audio_level():
    global rms
    j = {"id": 1, "jsonrpc": "2.0", "result": f"{rms}"}
    return j


def recognize_audio(file1, recording_data):
    y1, sr1 = load_audio_file(file1)
    # y2, sr2 = load_audio_file(file2)
    y2 = np.frombuffer(b''.join(recording_data), dtype=np.float32)
    similarity = 1 - cosine(y1[:len(y2)], y2)
    return similarity


def load_audio_file(file_path):
    y, sr = sf.read(file_path)
    if len(y.shape) > 1:  # Sprawdzenie czy dane audio są wielokanałowe
        y = np.mean(y, axis=1)  # Konwersja na jednokanałowe, jeśli są wielokanałowe
    return y, sr
