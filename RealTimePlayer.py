import time
import signal
import pyaudio
import numpy as np
import threading
import wave
import audioop
import math
from sklearn.metrics.pairwise import cosine_similarity
from scipy.interpolate import interp1d
import librosa.feature



class RealTimePlayer(threading.Thread):
    def __init__(self, input_device_id, output_device_id):
        threading.Thread.__init__(self)
        self.dtype = np.int32
        self.patype = pyaudio.paInt32
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
        self.data = np.zeros(1000000, dtype=self.dtype)
        self.recording = []
        self.rms = 0
        self.db = 0
        self.audio_status = False
        self.rec_path = 'file.wav'
        self.similarity = 0
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
                raw_data = np.fromstring(data, dtype=self.dtype)
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
        val = np.frombuffer(val, dtype=self.dtype)
        c = self.CHUNK
        self.data[:-c] = self.data[c:]
        self.data[-c:] = val
        # self.data = val

    def create_input_stream(self):
        self.stream = self.p.open(format=self.patype, channels=1, rate=self.RATE, input=True,
                                  input_device_index=self.input_device_id, frames_per_buffer=self.CHUNK)

    def create_output_stream(self):
        self.player = self.p.open(format=self.patype, channels=1, rate=self.RATE, output=True,
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

        # filtered_recording = self.apply_lowpass_filter(self.recording)

        print('Creating wave file')
        wave_file = wave.open(rec_path, 'wb')
        wave_file.setnchannels(1)
        wave_file.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wave_file.setframerate(self.RATE)
        wave_file.writeframes(b''.join(self.recording))
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

    def check_audio_is_available(self, mute_level):
        self.audio_status = False if float(self.rms) < float(mute_level) else True
        return self.audio_status

    def calculate_audio_freq(self):
        fft_data = np.abs(np.fft.rfft(self.data))
        max_index = np.argmax(fft_data[1:]) + 1

        if max_index != len(fft_data) - 1:
            x_values = np.arange(max_index - 1, max_index + 2)
            y_values = np.log(fft_data[x_values])

            interp_func = interp1d(x_values, y_values, kind='quadratic')
            interpolated_max_index = interp_func(max_index)

            interpolated_freq = (max_index + interpolated_max_index) * self.RATE / self.CHUNK
            return int(interpolated_freq)
        else:
            max_freq = max_index * self.RATE / self.CHUNK
            return int(max_freq)

    def load_audio_file(self, file_path):
        y, sr = librosa.load(file_path)
        return y, sr

    def calculate_features(self, data, sample_rate):
        mfcc = librosa.feature.mfcc(y=data, sr=sample_rate, n_mfcc=20)
        chroma = librosa.feature.chroma_stft(y=data, sr=sample_rate)
        tempo = librosa.feature.tempo(y=data, sr=sample_rate)[0]
        # zcr = librosa.feature.zero_crossing_rate(y=data)
        # spectral_centroid = librosa.feature.spectral_centroid(y=data, sr=sample_rate)
        # spectral_bandwidth = librosa.feature.spectral_bandwidth(y=data, sr=sample_rate)
        # rms_energy = librosa.feature.rms(y=data)
        # return [mfcc, chroma, tempo, zcr, spectral_centroid, spectral_bandwidth, rms_energy]
        return [mfcc, chroma, tempo]

    def calculate_similarity(self, feature1, feature2):
        if isinstance(feature1, (int, float)) and isinstance(feature2, (int, float)):
            distance = abs(feature1 - feature2)
            max_distance = max(feature1, feature2)
            similarity_percentage = max(1 - distance / max_distance, 0) * 100
            return similarity_percentage
        min_frames = min(feature1.shape[1], feature2.shape[1])
        feature1 = feature1[:, :min_frames]
        feature2 = feature2[:, :min_frames]
        similarity_matrix = cosine_similarity(feature1.T, feature2.T)
        return np.mean(similarity_matrix)*100

    def recognize_audio(self, file1, recording_data):
        y1, sr1 = self.load_audio_file(file1)
        y2 = np.frombuffer(b''.join(recording_data), dtype=self.dtype)
        # Convert audio data to floating point
        y1_float = librosa.util.normalize(y1.astype(np.float32))
        y2_float = librosa.util.normalize(y2.astype(np.float32))

        features1 = self.calculate_features(y1_float, sr1)
        features2 = self.calculate_features(y2_float, sr1)

        features_name = ['MFCC', 'Chroma', 'Tempo']
        similarity = []
        for f1, f2 in zip(features1, features2):
            sim = self.calculate_similarity(f1, f2)
            similarity.append(sim)
            print(f'Similarity = {sim}')
        self.similarity = dict(zip(features_name, similarity))
        return self.similarity








