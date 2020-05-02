from psop import *
import pyaudio
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget

instrument = Synth()

p = pyaudio.PyAudio()


def callback(in_data, frame_count, time_info, status):
    data = np.asarray(instrument.get_samples(frame_count), dtype=np.float32)
    return (data, pyaudio.paContinue)
    
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=48000,
                output=True,
                stream_callback=callback)
stream.start_stream()

input()
instrument.release()
input()
stream.stop_stream()
stream.close()

p.terminate()
