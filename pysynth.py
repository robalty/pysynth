from psop import *
import pyaudio
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget
import mido

instrument = Synth()
p = pyaudio.PyAudio()
mido.set_backend('mido.backends.rtmidi/LINUX_ALSA')


def callback(in_data, frame_count, time_info, status):
    data = np.asarray(instrument.get_samples(frame_count), dtype=np.float32)
    return (data, pyaudio.paContinue)
    
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=48000,
                output=True,
                stream_callback=callback)
stream.start_stream()

inport = mido.open_input(mido.get_input_names()[0])
playing = 0
pfreq = 0
for msg in inport:
    if msg.type == 'note_on':
        playing = msg.note
        instrument.press()
        pfreq = (2 ** ((playing - 69) / 12)) * 440
        instrument.set_freq(pfreq)
        instrument.set_vol(msg.velocity)
    elif msg.type == 'note_off':
        if msg.note == playing:
            instrument.release()
    elif msg.type == 'pitchwheel':
        mod = (msg.pitch  + 32768) / 32768
        x = pfreq * mod
        instrument.set_freq(x)
    else:
        print(msg)
stream.stop_stream()
stream.close()

p.terminate()
