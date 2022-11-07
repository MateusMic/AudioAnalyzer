import pyaudio
import numpy as np
import threading
import audioop


class RealTimePlayer(threading.Thread):
    def __init__(self, input_device_id=4, output_device_id=7):
        threading.Thread.__init__(self)
        self.input_device_id = input_device_id
        self.output_device_id = output_device_id
        self.name = 'RealTimePlayer'
        self.state = False
        self.player_state = False
        # self.CHUNK = 1024
        self.CHUNK = 1024
        self.RATE = 44100
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.player = None
        self.data = np.zeros(1000000, dtype=np.int32)

    def __del__(self):
        print("Destructor")
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def run(self):
        self.create_input_stream()
        self.create_output_stream()
        while self.state:
            self.raw_data = np.fromstring(self.stream.read(self.CHUNK), dtype=np.int16)
            self.append(self.raw_data)
            if self.player_state:
                self.player.write(self.raw_data, self.CHUNK)
        self.data = []

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

# player = RealTimePlayer(4, 7)
# player.state = 1
# player.start()










