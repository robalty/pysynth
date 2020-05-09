from psop import *
from gui import *
import pyaudio
import numpy as np
import mido
import sys
from PyQt5.QtCore import *

class PySynth(QRunnable):

    def __init__(self):
        super(PySynth, self).__init__()
        self.instrument = Synth()
        self.p = pyaudio.PyAudio()
        mido.set_backend('mido.backends.rtmidi/LINUX_ALSA')
        
        #VARIABLES:
        self.cur_note = 0
        self.cur_freq = 0
        self.cur_vol = 0
        self.cur_pitch = 1
        self.global_vol = 128


    def callback(self, in_data, frame_count, time_info, status):
        data = np.asarray(self.instrument.get_samples(frame_count), dtype=np.int16)
        return (data, pyaudio.paContinue)
    
    def run(self): 
        stream = self.p.open(format=pyaudio.paInt16,
                channels=1,
                rate=48000,
                output=True,
                stream_callback=self.callback)
        stream.start_stream()

        inport = mido.open_input(mido.get_input_names()[0])

        for msg in inport:
            if msg.type == 'note_on':
                self.cur_note = msg.note
                self.instrument.press()
                self.cur_freq = (2 ** ((self.cur_note - 69) / 12)) * 440
                self.instrument.set_freq(self.cur_freq * self.cur_pitch)
                self.cur_vol = msg.velocity
                self.instrument.vol = self.cur_vol * self.global_vol
            elif msg.type == 'note_off':
                if msg.note == self.cur_note:
                    self.instrument.release()
            elif msg.type == 'pitchwheel':
                #pitch bend - 1 octave range
                self.cur_pitch = 2 ** (msg.pitch / 8192)
                x = self.cur_freq * self.cur_pitch
                self.instrument.set_freq(x)
            elif msg.type == 'control_change':
                if msg.control == 7:
                    #volume knob
                    self.global_vol = msg.value
                    self.instrument.vol = self.global_vol * self.cur_vol
            elif msg.control == 3:
                #next algorithm (ff on my keyboard)
                if msg.value != 0:
                    self.instrument.algorithm = (self.instrument.algorithm + 1) % 9
                    print(self.instrument.algorithm)
            elif msg.control == 2:
                #prev algorithm (rw on my keyboard)
                if msg.value != 0:
                    self.instrument.algorithm = (self.instrument.algorithm - 1) % 9
                    print(self.instrument.algorithm)
            elif msg.control == 1:
                #feedback amount on op[0] - mod wheel
                t = (msg.value - 64) * (512 / np.pi)
                self.instrument.ops[0].modulation = (msg.value - 64) * (8192 / np.pi)
            else:
                print(msg)
        else:
            print(msg)
        stream.stop_stream()
        stream.close()

        self.p.terminate()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    threadpool = QThreadPool()
    window = GUI()
    synth = PySynth()
    threadpool.start(synth)

    sys.exit(app.exec_())
    
