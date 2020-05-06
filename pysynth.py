from psop import *
import pyaudio
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget
import mido

instrument = Synth()
instrument2 = Synth()
p = pyaudio.PyAudio()
mido.set_backend('mido.backends.rtmidi/LINUX_ALSA')


def callback(in_data, frame_count, time_info, status):
    data = np.asarray(instrument.get_samples(frame_count), dtype=np.int16)
    return (data, pyaudio.paContinue)
    
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=48000,
                output=True,
                stream_callback=callback)
stream.start_stream()

inport = mido.open_input(mido.get_input_names()[0])
playing = 0
pfreq = 0
nvol = 0
gvol = 128
for msg in inport:
    if msg.type == 'note_on':
        playing = msg.note
        instrument.press()
        pfreq = (2 ** ((playing - 69) / 12)) * 440
        instrument.set_freq(pfreq)
        nvol = msg.velocity
        instrument.vol = nvol * gvol
    elif msg.type == 'note_off':
        if msg.note == playing:
            instrument.release()
    elif msg.type == 'pitchwheel':
        mod = 1 + (msg.pitch / 32768)
        x = pfreq * mod
        instrument.set_freq(x)
    elif msg.type == 'control_change':
        if msg.control == 7:
            gvol = msg.value
            instrument.vol = gvol * nvol
        elif msg.control == 3:
            if msg.value != 0:
                instrument.algorithm = (instrument.algorithm + 1) % 9
                print(instrument.algorithm)
        elif msg.control == 2:
            if msg.value != 0:
                instrument.algorithm = (instrument.algorithm - 1) % 9
                print(instrument.algorithm)
        elif msg.control == 1:
            instrument.ops[0].modulation = (msg.value - 64) / 32
        else:
            print(msg)
    else:
        print(msg)
stream.stop_stream()
stream.close()

p.terminate()
