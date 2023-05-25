import pyaudio
import numpy as np
import threading
import wave


class RealTimePlayer(threading.Thread):
    def __init__(self, input_device_id=4, output_device_id=7):
        threading.Thread.__init__(self)
        self.input_device_id = input_device_id
        self.output_device_id = output_device_id
        self.name = 'RealTimePlayer'
        self.state = False
        self.output_state = False
        self.recording_state = False
        # self.CHUNK = 1024
        self.CHUNK = 1024
        self.RATE = 44100
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.player = None
        self.data = np.zeros(1000000, dtype=np.int32)
        self.recording = []
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
                raw_data = np.fromstring(data, dtype=np.int16)
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
        val = np.frombuffer(val, 'int16')
        c = self.CHUNK
        self.data[:-c] = self.data[c:]
        self.data[-c:] = val
        # self.data = val

    def create_input_stream(self):
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=self.RATE, input=True,
                                  input_device_index=self.input_device_id, frames_per_buffer=self.CHUNK)

    def create_output_stream(self):
        self.player = self.p.open(format=pyaudio.paInt16, channels=1, rate=self.RATE, output=True,
                                  output_device_index=self.output_device_id, frames_per_buffer=self.CHUNK)

    def start_recording(self):
        self.recording = []
        self.recording_state = True

    def stop_recording(self):
        self.recording_state = False
        print('Creating wave file')
        wave_file = wave.open("file.wav", 'wb')
        wave_file.setnchannels(1)
        wave_file.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wave_file.setframerate(self.RATE)
        wave_file.writeframes(b''.join(self.recording))
        wave_file.close()










