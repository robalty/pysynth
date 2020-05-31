from decimal import Decimal, Context, setcontext
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QDial, QComboBox, QGridLayout, QFrame
from PyQt5.QtGui import QPixmap

# Since Qt only accepts integer values, we need an array to handle
# floats values
float_array = list()
control_context = Context(prec=2)
setcontext(control_context)
j = Decimal(0.0)
for i in range(101):
    float_array.append(j.normalize())
    j += Decimal(0.1)


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

        # Volume label
        self.label = QLabel("Volume")
        self.label.setAlignment(Qt.AlignCenter)

        # Value display (updates on value change)
        self.val_display = QLabel("100")
        self.val_display.setAlignment(Qt.AlignCenter)
        self.val_display.setFrameStyle(QFrame.StyledPanel)

        self.setNotchesVisible(True)
        self.setRange(0, 128)
        self.setValue(100)
        self.valueChanged.connect(lambda: self.vol_change(synth))

    def vol_change(self, synth):
        synth.global_vol = self.value()
        self.val_display.setNum(self.value())


class OpFreqControl(QDial):
    def __init__(self, synth, op):
        super(OpFreqControl, self).__init__()

        # Value display updates on dial change
        self.val_display = QLabel("1")
        self.val_display.setAlignment(Qt.AlignCenter)
        self.val_display.setFrameStyle(QFrame.StyledPanel)

        self.setNotchesVisible(True)
        self.setRange(1, 16)
        self.setValue(1)
        self.valueChanged.connect(lambda: self.op_freq_change(synth, op))

    def op_freq_change(self, synth, op):
        synth.instrument.ops[op].freq_mult = self.value()
        self.val_display.setNum(self.value())


class OpModControl(QDial):
    def __init__(self, synth, op):
        super(OpModControl, self).__init__()

        # Value display updates on dial change
        self.val_display = QLabel("0")
        self.val_display.setAlignment(Qt.AlignCenter)
        self.val_display.setFrameStyle(QFrame.StyledPanel)

        self.setRange(0, 100)
        self.valueChanged.connect(lambda: self.op_mod_change(synth, op))

    def op_mod_change(self, synth, op):
        synth.instrument.ops[op].mod = float(float_array[self.value()])
        self.val_display.setNum(float(float_array[self.value()]))


class PitchControl(QDial):
    def __init__(self, synth):
        super(PitchControl, self).__init__()

        # Global pitch control label
        self.label = QLabel("Pitch Adjustment")
        self.label.setAlignment(Qt.AlignCenter)

        # Global pitch value display
        self.val_display = QLabel("0")
        self.val_display.setAlignment(Qt.AlignCenter)
        self.val_display.setFrameStyle(QFrame.StyledPanel)

        self.setNotchesVisible(True)
        self.setRange(-5, 5)
        self.valueChanged.connect(lambda: self.pitch_change(synth))

    def pitch_change(self, synth):
        synth.semi_shift = self.value() * 100
        if self.value() > 0:
            self.val_display.setText("+" + str(self.value()))
        else:
            self.val_display.setNum(self.value())


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

        # Operator frequency control dials
        self.op_a_freq = OpFreqControl(self.synth, 0)
        self.op_b_freq = OpFreqControl(self.synth, 1)
        self.op_c_freq = OpFreqControl(self.synth, 2)
        self.op_d_freq = OpFreqControl(self.synth, 3)

        # Operator mod control dials
        self.op_a_mod = OpModControl(self.synth, 0)
        self.op_b_mod = OpModControl(self.synth, 1)
        self.op_c_mod = OpModControl(self.synth, 2)
        self.op_d_mod = OpModControl(self.synth, 3)

        self.init_gui()

    def init_gui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        layout = QGridLayout()

        # Create the splash image widget
        label = QLabel(self)
        pixmap = QPixmap('synthwave.jpg')
        label.setPixmap(pixmap)

        # Splash image
        layout.addWidget(label, 0, 0, 1, 4)

        # Synth title
        layout.addWidget(self.synth_label, 1, 0)

        # Algorithm selector
        layout.addWidget(self.alg_a, 2, 0)

        # Synth volume control
        layout.addWidget(self.vol_a.label, 1, 1)
        layout.addWidget(self.vol_a.val_display, 2, 1)
        layout.addWidget(self.vol_a, 3, 1)

        # Pitch control
        layout.addWidget(self.pitch_a.label, 1, 2)
        layout.addWidget(self.pitch_a.val_display, 2, 2)
        layout.addWidget(self.pitch_a, 3, 2)

        # Per operator labels
        for i in range(4):
            char = "A"
            j = chr(ord(char) + i)
            op_label = QLabel(f"Operator {j}")
            op_label.setAlignment(Qt.AlignCenter)
            op_label.setFrameStyle(QFrame.Panel | QFrame.Raised)
            op_label.setLineWidth(5)
            layout.addWidget(op_label, 4, i)

        # Per operator frequency controls
        for i in range(4):
            freq_label = QLabel("Frequency")
            freq_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(freq_label, 5, i)
        layout.addWidget(self.op_a_freq.val_display, 6, 0)
        layout.addWidget(self.op_a_freq, 7, 0)
        layout.addWidget(self.op_b_freq.val_display, 6, 1)
        layout.addWidget(self.op_b_freq, 7, 1)
        layout.addWidget(self.op_c_freq.val_display, 6, 2)
        layout.addWidget(self.op_c_freq, 7, 2)
        layout.addWidget(self.op_d_freq.val_display, 6, 3)
        layout.addWidget(self.op_d_freq, 7, 3)

        # Per operator mod controls
        for i in range(4):
            mod_label = QLabel("Mod")
            mod_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(mod_label, 8, i)
        layout.addWidget(self.op_a_mod.val_display, 9, 0)
        layout.addWidget(self.op_a_mod, 10, 0)
        layout.addWidget(self.op_b_mod.val_display, 9, 1)
        layout.addWidget(self.op_b_mod, 10, 1)
        layout.addWidget(self.op_c_mod.val_display, 9, 2)
        layout.addWidget(self.op_c_mod, 10, 2)
        layout.addWidget(self.op_d_mod.val_display, 9, 3)
        layout.addWidget(self.op_d_mod, 10, 3)

        self.setLayout(layout)

        self.show()

    # Overrides default close event signal to run the MIDI/audio stream shutdown sequence
    def closeEvent(self, event):
        self.synth.shutdown()
        event.accept()
