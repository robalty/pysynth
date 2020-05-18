from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QDial, QComboBox, QGridLayout
from PyQt5.QtGui import QPixmap


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
        # Volume control slider
        self.vol_label = QLabel("Volume")
        self.vol_label.setAlignment(Qt.AlignCenter)
        self.vol_slider = QDial()
        self.vol_slider.setNotchesVisible(True)
        self.vol_slider.setRange(0, 128)
        self.vol_slider.setValue(100)
        self.vol_slider.valueChanged.connect(self.volume_change)
        self.vol_label.setBuddy(self.vol_slider)

        # Instrument selector
        self.synth_label = QLabel("Synth 1")
        self.inst_select = QComboBox()
        for i in range(9):
            self.inst_select.addItem(f"Algorithm {i}")
        self.inst_select.currentIndexChanged.connect(lambda: self.inst_change(self.inst_select.currentIndex()))

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
        layout.addWidget(label, 0, 0, 1, 2)
        layout.addWidget(self.synth_label, 1, 0)
        layout.addWidget(self.inst_select, 2, 0)
        layout.addWidget(self.vol_label, 1, 1)
        layout.addWidget(self.vol_slider, 2, 1)
        self.setLayout(layout)

        self.show()

    def volume_change(self):
        self.synth.global_vol = self.vol_slider.value()

    def inst_change(self, selected):
        self.synth.instrument.algorithm = selected

    # Overrides default close event signal to run the MIDI/audio stream shutdown sequence
    def closeEvent(self, event):
        self.synth.shutdown()
        event.accept()
