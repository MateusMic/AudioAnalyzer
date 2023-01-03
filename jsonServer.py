import socket
import threading
import json
import AudioAnalyzer as AA



class jsonServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.sock = socket.socket()
        print("Socket created ...")
        self.port = 1500
        self.sock.bind(('', self.port))
        self.sock.listen(5)
        print('socket is listening')
        self.response = None
        self.method = {'getAudioState0': AA.get_audio_state}

    def run(self):
        while True:
            c, addr = self.sock.accept()
            print('got connection from ', addr)
            json_received = c.recv(1024)
            print("Json received -->", json_received)
            self.response = json.dumps(self.set_response(json.loads(json_received)))
            c.sendall(self.response.encode())
            print("Json response -->", self.response)
            c.close()

    def set_response(self, json_received: dict):
        met = json_received.get('method')
        f_met = self.method.get(met)
        return f_met()
        # {"jsonrpc": "2.0", "id": 1, "method": "getAudioState0", "params": 0}

t = jsonServer()
t.start()




