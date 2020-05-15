from pysynth import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import *


class GUI(QWidget):

    def __init__(self):
        super(GUI, self).__init__()

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

        # Objects and inits
        self.synth = PySynth()
        self.init_gui()

    def init_gui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        layout = QGridLayout()

        # Create the splash image widget
        label = QLabel(self)
        pixmap = QPixmap('synthwave.jpg')
        label.setPixmap(pixmap)

        # Instrument selector
        inst_select = QComboBox()
        inst_select.addItem('Synth 1')
        inst_select.addItem('Synth 2')

        # Set up the widget grid layout
        layout.addWidget(label, 0, 0)
        layout.addWidget(inst_select, 1, 0)
        layout.addWidget(self.vol_label, 2, 0)
        layout.addWidget(self.vol_slider, 3, 0)
        self.setLayout(layout)

        self.show()

    def volume_change(self):
        self.synth.global_vol = self.vol_slider.value()

    # Overrides default close event signal to run the MIDI/audio stream shutdown sequence
    def closeEvent(self, event):
        self.synth.shutdown()
        event.accept()
