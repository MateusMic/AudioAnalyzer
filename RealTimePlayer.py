import time
import signal
import pyaudio
import numpy as np
import threading
import wave
import audioop
import math



class RealTimePlayer(threading.Thread):
    def __init__(self, input_device_id, output_device_id):
        threading.Thread.__init__(self)
        self.input_device_id = input_device_id
        self.output_device_id = output_device_id
        self.name = 'RealTimePlayer'
        self.state = False
        self.output_state = False
        self.recording_state = False
        self.CHUNK = 1024
        self.RATE = 44100
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.player = None
        self.data = np.zeros(1000000, dtype=np.float32)
        self.recording = []
        self.rms = 0
        self.db = 0
        self.rec_path = 'file.wav'
        print('Instance Created')

    def __del__(self):
        print("Destructor")
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def run(self):
        try:
            self.create_input_stream()
            self.create_output_stream()
            while self.state:
                data = self.stream.read(self.CHUNK)
                raw_data = np.fromstring(data, dtype=np.float32)
                self.append(raw_data)
                if self.output_state:
                    self.player.write(raw_data, self.CHUNK)
                if self.recording_state:
                    self.recording.append(data)
        except OSError:
            print('*' * 30)
            print('OSError')
            print('*' * 30)
            self.run()

    def append(self, val):
        val = np.frombuffer(val, dtype=np.float32)
        c = self.CHUNK
        self.data[:-c] = self.data[c:]
        self.data[-c:] = val
        # self.data = val

    def create_input_stream(self):
        self.stream = self.p.open(format=pyaudio.paFloat32, channels=1, rate=self.RATE, input=True,
                                  input_device_index=self.input_device_id, frames_per_buffer=self.CHUNK)

    def create_output_stream(self):
        self.player = self.p.open(format=pyaudio.paInt16, channels=1, rate=self.RATE, output=True,
                                  output_device_index=self.output_device_id, frames_per_buffer=self.CHUNK)

    def start_recording(self):
        self.recording = []
        self.recording_state = True
        return True

    def stop_recording(self):
        self.recording_state = False

    def save_recording_to_file(self, rec_path):
        if self.rec_path == '':
            print('Set proper recording path before start')
            return False

        filtered_recording = self.apply_lowpass_filter(self.recording)

        print('Creating wave file')
        wave_file = wave.open(rec_path, 'wb')
        wave_file.setnchannels(1)
        wave_file.setsampwidth(self.p.get_sample_size(pyaudio.paFloat32))
        wave_file.setframerate(self.RATE)
        wave_file.writeframes(b''.join(self.filtered_recording))
        wave_file.close()
        return True

    def apply_lowpass_filter(self, recording, cutoff_frequency=4000):
        # Obliczanie współczynnika filtru dolnoprzepustowego
        nyquist_frequency = 0.5 * self.RATE
        normalized_cutoff = cutoff_frequency / nyquist_frequency
        filter_order = 3  # Stopień filtru

        # Tworzenie współczynników filtra
        b, a = signal.butter(filter_order, normalized_cutoff, btype='low', analog=False)

        # Filtracja nagrania
        filtered_recording = signal.filtfilt(b, a, recording)

        return filtered_recording

    def calc_rms(self):
        self.rms = audioop.rms(self.data[-self.CHUNK:], 2) / 32767
        return self.rms

    def calc_db(self):
        self.db = 20 * math.log10(self.rms)
        return int(self.db)







