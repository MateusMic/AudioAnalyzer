from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import pyqtgraph as pg
import sys
import AudioAnalyzer as AA
import RealTimePlayer as rtp
import threading
import time


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.player = rtp.RealTimePlayer()

        self.setWindowTitle("Audio analyzer")

        main_layout = QVBoxLayout()
        source_selection_layout = QHBoxLayout()
        main_layout.addLayout(source_selection_layout)

        source_selection_layout_widget_list = []

        audio_input_selection_label = QLabel()
        audio_input_selection_label.setText('Select input device')
        source_selection_layout_widget_list.append(audio_input_selection_label)

        self.audio_input_selection = QComboBox()
        self.audio_input_selection.addItems(AA.get_audio_input_list())
        source_selection_layout_widget_list.append(self.audio_input_selection)

        audio_output_selection_label = QLabel()
        audio_output_selection_label.setText('Select output device')
        source_selection_layout_widget_list.append(audio_output_selection_label)

        self.audio_output_selection = QComboBox()
        self.audio_output_selection.addItems(AA.get_audio_output_list())
        source_selection_layout_widget_list.append(self.audio_output_selection)

        self.play_button = QPushButton()
        self.play_button.setIcon(QIcon(r'C:\Users\mjl2yj\PycharmProjects\AudioRecognizer\icons\playButton.jpg'))
        self.play_button.setText('Play')
        self.play_button.clicked.connect(self.play_button_state_change)
        source_selection_layout_widget_list.append(self.play_button)

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

    def play(self):
        self.player.input_device_id = self.get_selected_input()
        self.player.output_device_id = self.get_selected_output()
        self.player.state = True
        self.player.start()
        time.sleep(0.5)
        # update graph widget
        self.timer.start(100)
        # update data label widget
        self.timer2.start(100)
        self.play_button.setText('Pause')
        self.play_button.setIcon(QIcon(r'C:\Users\mjl2yj\PycharmProjects\AudioRecognizer\icons\pauseButton.jpg'))

    def stop(self):
        self.player.state = False
        # Stop update graph widget
        self.timer.stop()
        # Stop update data label widget
        self.timer2.stop()
        self.play_button.setText('Play')
        self.play_button.setIcon(QIcon(r'C:\Users\mjl2yj\PycharmProjects\AudioRecognizer\icons\playButton.jpg'))

    def play_button_state_change(self):
        if self.player.state == 1:
            self.stop()
        else:
            self.play()

    def update_graph_widget(self):
        self.graphWidget.plotItem.clear()
        self.graphWidget.plot(self.player.data, pen='b')

    def update_data_label(self):
        rms = AA.calculate_rms(self.player.data)
        db = AA.calculate_db(rms)
        freq = AA.calculate_audio_freq(self.player)
        audio_status = False if rms < 0.003 else True
        self.data_label.setText(self.label_text.format(rms, db, audio_status, freq))









app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()



