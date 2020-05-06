from psop import *
import pyaudio
import numpy as np
import mido

instrument = Synth()
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

#VARIABLES:
cur_note = 0
cur_freq = 0
cur_vol = 0
cur_pitch = 1
global_vol = 128
for msg in inport:
    if msg.type == 'note_on':
        cur_note = msg.note
        instrument.press()
        cur_freq = (2 ** ((cur_note - 69) / 12)) * 440
        instrument.set_freq(cur_freq * cur_pitch)
        cur_vol = msg.velocity
        instrument.vol = cur_vol * global_vol
    elif msg.type == 'note_off':
        if msg.note == cur_note:
            instrument.release()
    elif msg.type == 'pitchwheel':
        #pitch bend - 1 octave range
        cur_pitch = 2 ** (msg.pitch / 8192)
        x = cur_freq * cur_pitch
        instrument.set_freq(x)
    elif msg.type == 'control_change':
        if msg.control == 7:
            #volume knob
            global_vol = msg.value
            instrument.vol = global_vol * cur_vol
        elif msg.control == 3:
            #next algorithm (ff on my keyboard)
            if msg.value != 0:
                instrument.algorithm = (instrument.algorithm + 1) % 9
                print(instrument.algorithm)
        elif msg.control == 2:
            #prev algorithm (rw on my keyboard)
            if msg.value != 0:
                instrument.algorithm = (instrument.algorithm - 1) % 9
                print(instrument.algorithm)
        elif msg.control == 1:
            #feedback amount on op[0] - mod wheel
            t = (msg.value - 64) * (512 / np.pi)
            instrument.ops[0].modulation = (msg.value - 64) * (8192 / np.pi)
        else:
            print(msg)
    else:
        print(msg)
stream.stop_stream()
stream.close()

p.terminate()
