from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QDial, QComboBox, QGridLayout
from PyQt5.QtGui import QPixmap


class AlgorithmSelector(QComboBox):
    def __init__(self, synth):
        super(AlgorithmSelector, self).__init__()
        for i in range(9):
            self.addItem(f"Algorithm {i}")
        self.currentIndexChanged.connect(lambda: self.algorithm_change(synth))

    def algorithm_change(self, synth):
        synth.instrument.algorithm = self.currentIndex()


class VolumeControl(QDial):
    def __init__(self, synth):
        super(VolumeControl, self).__init__()
        self.label = QLabel("Volume")
        self.label.setAlignment(Qt.AlignCenter)
        self.setNotchesVisible(True)
        self.setRange(0, 128)
        self.setValue(100)
        self.valueChanged.connect(lambda: self.vol_change(synth))
        self.label.setBuddy(self)

    def vol_change(self, synth):
        synth.global_vol = self.value()


class PitchControl(QDial):
    def __init__(self, synth):
        super(PitchControl, self).__init__()
        self.label = QLabel("Pitch")
        self.label.setAlignment(Qt.AlignCenter)
        self.setNotchesVisible(True)
        self.setRange(-5, 5)
        self.valueChanged.connect(lambda: self.pitch_change(synth))

    def pitch_change(self, synth):
        synth.cur_pitch = self.value()


class GUI(QWidget):

    def __init__(self):
        super(GUI, self).__init__()
        from pysynth import PySynth
        self.synth = PySynth()

        # Window environment variables
        self.title = 'PySynth - Feel the wave'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480

        # QObject Inits and Connections
        # Synth labels
        self.synth_label = QLabel("Synth 1")

        # Algorithm selector
        self.alg_a = AlgorithmSelector(self.synth)

        # Volume control dial
        self.vol_a = VolumeControl(self.synth)

        # Pitch control dial
        self.pitch_a = PitchControl(self.synth)

        self.init_gui()

    def init_gui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        layout = QGridLayout()

        # Create the splash image widget
        label = QLabel(self)
        pixmap = QPixmap('synthwave.jpg')
        label.setPixmap(pixmap)

        # Set up the widget grid layout
        layout.addWidget(label, 0, 0, 1, 3)
        layout.addWidget(self.synth_label, 1, 0)
        layout.addWidget(self.alg_a, 2, 0)
        layout.addWidget(self.vol_a.label, 1, 1)
        layout.addWidget(self.vol_a, 2, 1)
        layout.addWidget(self.pitch_a.label, 1, 2)
        layout.addWidget(self.pitch_a, 2, 2)
        self.setLayout(layout)

        self.show()

    # Overrides default close event signal to run the MIDI/audio stream shutdown sequence
    def closeEvent(self, event):
        self.synth.shutdown()
        event.accept()
