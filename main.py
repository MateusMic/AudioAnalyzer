from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import pyqtgraph as pg
import sys
import RealTimePlayer as rtp
import time
import pyaudio
import threading
from jsonServer import jsonServer
from numpy import mean
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.player = None

        self.setWindowTitle("Audio analyzer")

        main_layout = QVBoxLayout()

        layout_list = []

        source_selection_layout = QHBoxLayout()
        listening_layout = QHBoxLayout()
        recording_layout = QHBoxLayout()
        output_layout = QHBoxLayout()
        mute_level_layout = QHBoxLayout()
        recognize_audio_layout = QHBoxLayout()

        layout_list.append(source_selection_layout)
        layout_list.append(listening_layout)
        layout_list.append(output_layout)
        layout_list.append(recording_layout)
        layout_list.append(recognize_audio_layout)
        layout_list.append(mute_level_layout)

        for layout in layout_list:
            main_layout.addLayout(layout)

        source_selection_layout_widget_list = []
        listening_layout_widget_list = []
        recording_layout_widget_list = []
        output_layout_widget_list = []
        config_layout_widget_list = []
        recognize_audio_layout_widget_list = []

        audio_input_selection_label = QLabel()
        audio_input_selection_label.setText('Select input device')
        source_selection_layout_widget_list.append(audio_input_selection_label)

        default_input_index = 2
        self.audio_input_selection = QComboBox()
        self.audio_input_selection.addItems(self.get_audio_input_list())
        source_selection_layout_widget_list.append(self.audio_input_selection)
        self.audio_input_selection.setCurrentIndex(default_input_index)


        audio_output_selection_label = QLabel()
        audio_output_selection_label.setText('Select output device')
        source_selection_layout_widget_list.append(audio_output_selection_label)

        default_output_index = 1
        self.audio_output_selection = QComboBox()
        self.audio_output_selection.addItems(self.get_audio_output_list())
        source_selection_layout_widget_list.append(self.audio_output_selection)
        self.audio_output_selection.setCurrentIndex(default_output_index)

        self.output_status_label = QLabel()
        self.output_status_label.setText('Output status')
        output_layout_widget_list.append(self.output_status_label)

        self.output_status_button = QPushButton()
        self.output_status_button.setText('Turn ON')
        self.output_status_button.clicked.connect(self.output_state_change)
        output_layout_widget_list.append(self.output_status_button)

        self.listening_label = QLabel()
        self.listening_label.setText('Listening')
        listening_layout_widget_list.append(self.listening_label)

        self.start_listening_button = QPushButton()
        self.start_listening_button.setText('Start')
        self.start_listening_button.clicked.connect(self.listening_state_change)
        listening_layout_widget_list.append(self.start_listening_button)

        self.recording_label = QLabel()
        self.recording_label.setText('Recording')
        recording_layout_widget_list.append(self.recording_label)

        self.start_recording_button = QPushButton()
        self.start_recording_button.setText('Start')
        self.start_recording_button.clicked.connect(self.recording_state_change)
        recording_layout_widget_list.append(self.start_recording_button)

        self.recognize_label = QLabel()
        self.recognize_label.setText('Set Compare File')
        recognize_audio_layout_widget_list.append(self.recognize_label)

        self.compare_file_path = QLineEdit()
        self.compare_file_path.setText(rf'{os.getcwd()}\file.wav')
        recognize_audio_layout_widget_list.append(self.compare_file_path)

        self.similarity_label = QLabel()
        self.similarity_label.setText('Similarity=-11')
        recognize_audio_layout_widget_list.append(self.similarity_label)

        self.start_recognize_button = QPushButton()
        self.start_recognize_button.setText('Compare')
        self.start_recognize_button.clicked.connect(self.start_compering_audio)
        recognize_audio_layout_widget_list.append(self.start_recognize_button)

        self.graphWidget = pg.PlotWidget()
        self.graphWidget.hideAxis('left')
        self.graphWidget.hideAxis('bottom')
        self.graphWidget.scale(100, 10)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_graph_widget)

        self.label_text = 'RMS:\t\t{}\nDB:\t\t{}\nAudio available:\t{}\nFrequency:\t{}'
        self.data_label = QLabel()
        self.data_label.setText(self.label_text.format(0, 0, False, 0))
        self.timer2 = QTimer()
        self.timer2.timeout.connect(self.update_data_label)

        self.mute_level_label = QLabel()
        self.mute_level_label.setText('Set Mute level')
        config_layout_widget_list.append(self.mute_level_label)
        self.mute_level = QLineEdit()
        self.mute_level.setText('0.00005')
        config_layout_widget_list.append(self.mute_level)
        self.rec_path_label = QLabel()
        self.rec_path_label.setText('Set path for recording')
        config_layout_widget_list.append(self.rec_path_label)
        self.rec_path = QLineEdit()
        self.rec_path.setText(rf'{os.getcwd()}\file.wav')
        self.rec_path.textChanged.connect(self.set_recording_path)
        config_layout_widget_list.append(self.rec_path)


        for w in source_selection_layout_widget_list:
            source_selection_layout.addWidget(w)

        for w in listening_layout_widget_list:
            listening_layout.addWidget(w)

        for w in output_layout_widget_list:
            output_layout.addWidget(w)

        for w in recording_layout_widget_list:
            recording_layout.addWidget(w)

        for w in config_layout_widget_list:
            mute_level_layout.addWidget(w)

        for w in recognize_audio_layout_widget_list:
            recognize_audio_layout.addWidget(w)

        main_layout.addWidget(self.graphWidget)
        main_layout.addWidget(self.data_label)

        widget = QWidget()
        widget.setLayout(main_layout)

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(widget)

    def get_selected_input(self):
        input = self.audio_input_selection.currentText()
        input_index = int(input[:input.find('-')])
        return input_index

    def get_selected_output(self):
        output = self.audio_output_selection.currentText()
        output_index = int(output[:output.find('-')])
        return output_index

    def start_listening(self):
        print('Start listening')
        self.player = rtp.RealTimePlayer(input_device_id=self.get_selected_input(),
                                         output_device_id=self.get_selected_output())
        self.player.state = True
        self.player.rec_path = self.rec_path.text() if self.rec_path.text() != '' else self.player.rec_path
        self.player.start()
        time.sleep(0.5)
        # update graph widget
        self.timer.start(100)
        # update data label widget
        self.timer2.start(100)
        self.start_listening_button.setText('Stop')

    def start_recording(self):
        print('Start recording')
        self.player.start_recording()
        self.start_recording_button.setText('Stop')

    def start_output(self):
        print('Start output streaming')
        self.player.output_state = True
        self.output_status_button.setText('Turn OFF')

    def stop_listening(self):
        print('Stop listening')
        self.player.state = False
        # Stop update graph widget
        self.timer.stop()
        # Stop update data label widget
        self.timer2.stop()
        self.start_listening_button.setText('Start')

    def stop_recording(self):
        print('Stop recording')
        self.player.stop_recording()
        self.player.save_recording_to_file(self.rec_path.text())
        self.start_recording_button.setText('Start')
        self.player.recording = []

    def stop_output(self):
        print('Stop output streaming')
        self.player.output_state = False
        self.output_status_button.setText('Turn ON')

    def listening_state_change(self):
        if self.player is None:
            self.start_listening()
        else:
            if self.player.state:
                self.stop_listening()
            else:
                self.start_listening()

    def recording_state_change(self):
        if 'player' not in vars(self):
            print('Cannot start recording. Object not created yet')
            return -1
        else:
            if self.player.recording_state:
                self.stop_recording()
            else:
                self.start_recording()

    def output_state_change(self):
        if 'player' not in vars(self):
            print('Cannot start output stream. Player object not created yet')
            return -1
        else:
            if self.player.output_state:
                self.stop_output()
            else:
                self.start_output()

    def update_graph_widget(self):
        self.graphWidget.plotItem.clear()
        self.graphWidget.plot(self.player.data, pen='b')

    def update_data_label(self):
        rtp_rms = self.player.calc_rms()
        db = self.player.calc_db()
        freq = self.player.calculate_audio_freq()
        audio_status = self.player.check_audio_is_available(self.mute_level.text())
        self.data_label.setText(self.label_text.format(rtp_rms, db, audio_status, freq))

    def start_compering_audio(self, t: int = 10):
        # self.player.recognize_state = True
        file_path1 = self.compare_file_path.text()
        thread = threading.Thread(target=self.compare_audio, args=(file_path1, t,))
        thread.start()
        thread.join()
        return self.player.similarity


    def record_sample(self, t):
        self.player.start_recording()
        time.sleep(t)
        self.player.stop_recording()

    def compare_audio(self, file_path1, t: int = 10):
        print('Compering...')
        self.record_sample(t)
        similarity = self.player.recognize_audio(file_path1, self.player.recording)
        self.player.recording = []
        sim = mean(list(similarity.values()))
        self.similarity_label.setText(f'Similarity={sim:.1f}%')
        return similarity

    def set_recording_path(self, path):
        if self.player:
            self.player.rec_path = self.rec_path.text()

    def get_audio_input_list(self):
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

    def get_audio_output_list(self):
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







app = QApplication(sys.argv)
window = MainWindow()
jsonServer = jsonServer(window)
jsonServer.start()
window.show()

app.exec()



