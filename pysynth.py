from PyQt5.QtCore import QRunnable
from PyQt5.QtWidgets import QApplication
from gui import GUI
from psop import *
import pyaudio
import numpy as np
import mido
import sys

NUM_INSTRUMENTS = 3
BUFFER_SIZE = 1024

class PySynth(QRunnable):

    def __init__(self):
        super(PySynth, self).__init__()


        self.instrument = []
        for i in range(0, NUM_INSTRUMENTS):
            self.instrument.append(Synth())
        self.p = pyaudio.PyAudio()
        self.buffer = np.empty(BUFFER_SIZE)
        mido.set_backend('mido.backends.rtmidi/LINUX_ALSA')

        # VARIABLES:
        self.cur = 0
        self.cur_keys = [0] * NUM_INSTRUMENTS
        self.cur_note = 0
        self.cur_freq = 0
        self.cur_vol = 0
        self.cur_pitch = 1
        self.semi_shift = 0
        self.global_vol = 128

        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=48000,
                                  output=True,
                                  stream_callback=self.audio_callback)
        self.stream.start_stream()

        self.inport = mido.open_input(mido.get_input_names()[0],
                                      callback=self.midi_callback)

    def audio_callback(self, in_data, frame_count, time_info, status):
        self.buffer = np.zeros(frame_count, dtype=np.int16)
        for i in range(0, NUM_INSTRUMENTS):
            self.buffer += np.asarray(self.instrument[i].get_samples(frame_count)/NUM_INSTRUMENTS, dtype=np.int16)
        return self.buffer, pyaudio.paContinue

    def midi_callback(self, msg):
        if msg.type == 'note_on':
            self.cur_note = msg.note
            self.instrument[self.cur].press()
            self.cur_freq = (2 ** (((self.cur_note - 69) + self.semi_shift) / 12)) * 440
            self.instrument[self.cur].set_freq(self.cur_freq * self.cur_pitch)
            self.cur_vol = msg.velocity
            self.instrument[self.cur].vol = self.cur_vol * self.global_vol
            if self.cur_keys[self.cur] != msg.note:
                self.cur_keys[self.cur] = msg.note
                self.cur = (self.cur + 1) % NUM_INSTRUMENTS
        elif msg.type == 'note_off':
            for i in range(0, NUM_INSTRUMENTS):
                if self.cur_keys[i] == msg.note:
                    self.instrument[i].release()
        elif msg.type == 'pitchwheel':
            # pitch bend - 1 octave range
            self.cur_pitch = 2 ** (msg.pitch / 8192)
            x = self.cur_freq * self.cur_pitch
            self.instrument[self.cur].set_freq(x)
        elif msg.type == 'control_change':
            if msg.control == 7:
                # volume knob
                self.global_vol = msg.value
                self.instrument[self.cur].vol = self.global_vol * self.cur_vol
            elif msg.control == 3:
                # increase op 0 mult (ff on my keyboard)
                if msg.value != 0:
                    temp = 1 + (self.instrument[self.cur].ops[0].freq_mult % 16)
                    self.instrument[self.cur].ops[0].freq_mult = temp
            elif msg.control == 2:
                # decrease op 0 mult (rw on my keyboard)
                if msg.value != 0:
                    temp = (self.instrument[self.cur].ops[0].freq_mult - 1) % 16
                    self.instrument[self.cur].ops[0].freq_mult = temp
            elif msg.control == 1:
                # feedback amount on op[0] - mod wheel
                t = (msg.value - 64) / 16
                self.instrument[self.cur].set_mod(t, 0)
        else:
            print(msg)

    def shutdown(self):
        self.inport.close()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GUI()
    sys.exit(app.exec_())
