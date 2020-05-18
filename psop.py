import math
import numpy as np

SAMPLERATE = 48000


class ADSR:
    def __init__(self, a=0.5, d=0.5, s=0.75, r=0.5):
        self.a = a
        self.d = d
        self.s = s
        self.r = r
        self.rvol = 0
        self.rtime = 0

    def get_vol(self, clock):
        if self.rtime != 0:
            return lerp(self.rvol, 0, clock - self.rtime, self.r)
        if clock < self.a:
            t = lerp(0, 1, clock, self.a)
            self.rvol = t
            return t
        elif clock < (self.a + self.d):
            t = lerp(1, self.s, clock, self.a + self.d)
            self.rvol = t
            return t
        else:
            return self.s

    def get_vols(self, clock, num):
        temp = []
        for i in range(num):
            temp.append(self.get_vol(clock + (i / SAMPLERATE)))
        return temp


class Operator:
    def __init__(self, i=SAMPLERATE, f=220, m=1):
        self.mod = 1
        self.frequency = f
        self.freq_mult = m
        self.envelope = ADSR()
        self.feedback = 0
        self.acc_phase = 0

    def sample(self, clock):
        return (self.frequency * clock) + self.acc_phase

    def sample_with(self, in_op, clock):
        return (self.frequency * clock) + (self.mod * in_op) + self.acc_phase


class Synth:
    def __init__(self):
        self.ops = [Operator(), Operator(), Operator(), Operator()]
        self.algorithm = 1
        self.clock = 0
        self.frequency = 220
        self.vol = 0

    def set_freq(self, val):
        self.frequency = val
        for i in self.ops:
            t = val * i.freq_mult * 2 * np.pi
            i.acc_phase += ((i.frequency - t) * self.clock)
            i.frequency = t

    def set_mod(self, val, op):
        self.ops[op].mod = val

    def get_samples(self, num_samples):
        temp = algtest(self.ops, self.clock, num_samples)
        self.clock += num_samples / SAMPLERATE
        return temp * self.vol

    def release(self):
        for op in self.ops:
            op.envelope.rtime = self.clock

    def press(self):
        self.clock = 0
        for op in self.ops:
            op.feedback = 0
            op.envelope.rvol = 0
            op.envelope.rtime = 0
            op.acc_phase = 0


def algtest(ops, clock, size):
    return alg1(ops, clock, size)


def samples(op, clock, size):
    first = np.sin(np.fromfunction(lambda x: op.sample(clock + (x / SAMPLERATE)), (size,)))
    vol = op.envelope.get_vols(clock, size)
    return np.multiply(vol, np.sin(first))


def samples_with(op, clock, size, in_op):
    first = np.fromfunction(lambda x: op.sample(clock + (x / SAMPLERATE)), (size,))
    vol = op.envelope.get_vols(clock, size)
    s_in = np.multiply(in_op, op.mod)
    return np.multiply(vol, np.sin(first + s_in))


def samples_fb(op, clock, size):
    temp = np.empty(size)
    temp[0] = np.sin(op.sample(clock) + (op.mod * op.feedback))
    for i in range(1, size):
        temp[i] = np.sin((op.mod * temp[i - 1]) + op.sample(clock + (i / SAMPLERATE)))
    op.feedback = temp[size - 1]
    tempvols = op.envelope.get_vols(clock, size)
    return np.multiply(temp, tempvols)


def alg1(ops, clock, size):
    first = samples_fb(ops[0], clock, size)
    second = samples_with(ops[1], clock, size, first)
    third = samples_with(ops[2], clock, size, second)
    return samples_with(ops[3], clock, size, third)


def lerp(startval, endval, time, endtime):
    if time > endtime:
        return endval
    else:
        temp = (endval - startval) * (time / endtime)
        return startval + temp
