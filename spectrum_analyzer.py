#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=bad-whitespace, invalid-name, missing-module-docstring
#
# Copyright (c) 2020 David Kim
#
# [This program is licensed under the "MIT License"]
# Please see the file LICENSE in the source
# distribution of this software for license terms.
#
# This Python script implements an audio spectrum analyzer.

import time
import struct
from scipy.fft import fft
import pyaudio
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
matplotlib.use("Qt5Agg")  # Setup QT5 backend

__author__ = 'David Kim'
__copyright__ = 'Copyright (c) 2020 David Kim'
__credits__ = ['David Kim']
__license__ = 'MIT'
__version__ = '1.0.0'
__maintainer__ = 'David Kim'
__email__ = 'djk3@pdx.edu'
__status__ = 'Production'

##############################################################################


class SpectrumAnalyzer:
    def __init__(self, p=None, stream=None):
        """ Constructor. """
        # Stream constants
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 48000
        self.CHUNK = 1024 * 2

        # Setup the stream
        if not p and not stream:
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                output=True,
                frames_per_buffer=self.CHUNK,
            )
        else:
            self.p = p
            self.stream = stream

        # Other constants
        self.fig = None
        self.line = None
        self.line_fft = None
        self.frame_count = None
        self.start_time = None
        self.should_exit = False

    def setup_analyzer(self):
        """ Setup the analyzer. """
        # Setup x variables for plotting
        x = np.arange(0, 2 * self.CHUNK, 2)
        xf = np.linspace(0, self.RATE, self.CHUNK)

        # Setup matplotlib figure and axes
        self.fig, (ax1, ax2) = plt.subplots(2, figsize=(15, 7))
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)

        # Setup a line object with random data
        self.line, = ax1.plot(x, np.random.rand(self.CHUNK), '-', lw=2)

        # Setup semilogx line for spectrum
        self.line_fft, = ax2.semilogx(
            xf, np.random.rand(self.CHUNK), '-', lw=2)

        # Format waveform axes
        ax1.set_title('AUDIO WAVEFORM')
        ax1.set_xlabel('samples')
        ax1.set_ylabel('volume')
        ax1.set_ylim(0, 255)
        ax1.set_xlim(0, 2 * self.CHUNK)
        plt.setp(
            ax1, yticks=[0, 128, 255],
            xticks=[0, self.CHUNK, 2 * self.CHUNK],
        )
        plt.setp(ax2, yticks=[0, 1],)

        # Format spectrum axes
        ax2.set_xlim(20, self.RATE / 2)

        # Show axes
        fig_manager = plt.get_current_fig_manager()
        fig_manager.window.setGeometry(10, 240, 640, 480)

        # Show analyzer
        plt.show(block=False)

    def start_analyzer(self):
        """ Start the analyzer. """
        print('stream started')
        self.frame_count = 0
        self.start_time = time.time()

        while not self.should_exit:
            data = self.stream.read(self.CHUNK, False)
            data_int = struct.unpack(str(2 * self.CHUNK) + 'B', data)
            data_np = np.array(data_int, dtype='b')[::2] + 128

            self.line.set_ydata(data_np)

            # Compute FFT and update line
            yf = fft(data_int)
            self.line_fft.set_ydata(
                np.abs(yf[0:self.CHUNK]) / (128 * self.CHUNK))

            # Update figure canvas
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            self.frame_count += 1

        # Exit the application
        self.exit()

    def onclick(self, event):
        """ Click event handler. """
        self.should_exit = True

    def exit(self):
        """ Close the stream and exit the application. """
        frame_rate = self.frame_count / (time.time() - self.start_time)
        print('average frame rate = {:.0f} FPS'.format(frame_rate))
        print('stream closed')
        self.p.close(self.stream)

    def start(self):
        self.setup_analyzer()
        self.start_analyzer()

##############################################################################


if __name__ == '__main__':
    s = SpectrumAnalyzer()
    s.start()
