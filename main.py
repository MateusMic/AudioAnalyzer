from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import pyqtgraph as pg
import sys
import AudioAnalyzer as AA
import RealTimePlayer as rtp
import time


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Audio analyzer")

        main_layout = QVBoxLayout()

        layout_list = []

        source_selection_layout = QHBoxLayout()
        listening_layout = QHBoxLayout()
        recording_layout = QHBoxLayout()
        output_layout = QHBoxLayout()

        layout_list.append(source_selection_layout)
        layout_list.append(listening_layout)
        layout_list.append(output_layout)
        layout_list.append(recording_layout)

        for layout in layout_list:
            main_layout.addLayout(layout)

        source_selection_layout_widget_list = []
        listening_layout_widget_list = []
        recording_layout_widget_list = []
        output_layout_widget_list = []

        audio_input_selection_label = QLabel()
        audio_input_selection_label.setText('Select input device')
        source_selection_layout_widget_list.append(audio_input_selection_label)

        default_index = AA.get_def_index()
        self.audio_input_selection = QComboBox()
        self.audio_input_selection.addItems(AA.get_audio_input_list())
        source_selection_layout_widget_list.append(self.audio_input_selection)
        self.audio_input_selection.setCurrentIndex(default_index)

        audio_output_selection_label = QLabel()
        audio_output_selection_label.setText('Select output device')
        source_selection_layout_widget_list.append(audio_output_selection_label)

        self.audio_output_selection = QComboBox()
        self.audio_output_selection.addItems(AA.get_audio_output_list())
        source_selection_layout_widget_list.append(self.audio_output_selection)

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

        for w in source_selection_layout_widget_list:
            source_selection_layout.addWidget(w)

        for w in listening_layout_widget_list:
            listening_layout.addWidget(w)

        for w in output_layout_widget_list:
            output_layout.addWidget(w)

        for w in recording_layout_widget_list:
            recording_layout.addWidget(w)

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
        self.player = rtp.RealTimePlayer()
        self.player.input_device_id = self.get_selected_input()
        self.player.output_device_id = self.get_selected_output()
        self.player.state = True
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
        self.start_recording_button.setText('Start')

    def stop_output(self):
        print('Stop output streaming')
        self.player.output_state = False
        self.output_status_button.setText('Turn ON')

    def listening_state_change(self):
        if 'player' not in vars(self):
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
        AA.rms = AA.calculate_rms(self.player.data)
        AA.db = AA.calculate_db(AA.rms)
        AA.freq = AA.calculate_audio_freq(self.player)
        AA.audio_status = False if AA.rms < 0.003 else True
        self.data_label.setText(self.label_text.format(AA.rms, AA.db, AA.audio_status, AA.freq))









app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()



