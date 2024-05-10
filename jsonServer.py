import socket
import threading
import json


class jsonServer(threading.Thread):
    def __init__(self, window):
        self.window = window
        threading.Thread.__init__(self)
        self.sock = socket.socket()
        # print("Socket created ...")
        self.port = 1698
        self.sock.bind(('', self.port))
        self.sock.listen(5)
        # print('socket is listening')
        self.response = None
        self.method = {'getAudioState0': self.get_audio_state,
                       'getAudioLevel0': self.get_audio_level,
                       'setRecordingPath': self.set_recording_path,
                       'startRecording': self.start_recording,
                       'stopRecording': self.stop_recording}

    def run(self):
        while True:
            c, addr = self.sock.accept()
            # print('got connection from ', addr)
            json_received = c.recv(1024)
            # print("Json received -->", json_received)
            self.response = json.dumps(self.set_response(json.loads(json_received)))
            c.sendall(self.response.encode())
            # print("Json response -->", self.response)
            c.close()

    def set_response(self, json_received: dict):
        met = json_received.get('method')
        f_met = self.method.get(met)
        return f_met(json_received)
        # {"jsonrpc": "2.0", "id": 1, "method": "getAudioState0", "params": 0}

    def get_audio_state(self, json_msg):
        if self.window.player.audio_status:
            j = {"id": 1, "jsonrpc": "2.0", "result": "audio"}
        else:
            j = {"id": 1, "jsonrpc": "2.0", "result": "mute"}
        return j

    def get_audio_level(self, json_msg):
        rms = self.window.player.rms
        j = {"id": 1, "jsonrpc": "2.0", "result": f"{rms}"}
        return j

    def set_recording_path(self, json_msg):
        path = json_msg.get('params')
        self.window.rec_path.setText(path)
        if self.window.rec_path.text() == path:
            j = {"id": 1, "jsonrpc": "2.0", "result": f"true"}
        else:
            j = {"id": 1, "jsonrpc": "2.0", "result": f"false"}
        return j

    def start_recording(self, json_msg):
        if self.window.player is None or self.window.player.recording_state:
            j = {"id": 1, "jsonrpc": "2.0", "result": f"false"}
            return j
        self.window.start_recording()
        if self.window.player.recording_state:
            j = {"id": 1, "jsonrpc": "2.0", "result": f"true"}
            return j
        else:
            j = {"id": 1, "jsonrpc": "2.0", "result": f"false"}
            return j

    def stop_recording(self, json_msg):
        if self.window.player is None or not self.window.player.recording_state:
            j = {"id": 1, "jsonrpc": "2.0", "result": f"false"}
            return j
        self.window.stop_recording()
        if not self.window.player.recording_state:
            j = {"id": 1, "jsonrpc": "2.0", "result": f"true"}
            return j
        else:
            j = {"id": 1, "jsonrpc": "2.0", "result": f"false"}
            return j