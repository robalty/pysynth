import math
import numpy as np

SAMPLERATE = 48000


class ADSR:
    def __init__(self, a=0.1, d=0.2, s=0.6, r=0.5):
        self.timings = {
                0 : 0,
                1 : 1 / ((a * SAMPLERATE) + 1),
                2 : -1 / ((d * SAMPLERATE) + 1),
                3 : 0,
                4 : -1 / ((r * SAMPLERATE) + 1)
                }
        self.s = s
        self.cur = 0
        self.stage = 0

    def get_vol(self):
        temp = self.cur + self.timings.get(self.stage)
        if temp > 0.99:
            temp = 0.99
            self.stage = 2
        elif (self.stage == 2) & (temp < self.s):
            temp = self.s
            self.stage = 3
        elif temp < 0:
            self.stage = 0
            return 0
        self.cur = temp
        return temp

    def get_vols(self, num):
        temp = []
        for i in range(num):
            temp.append(self.get_vol())
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
        func = alg.get(self.algorithm)
        temp = func(self.ops, self.clock, num_samples)
        self.clock += num_samples / SAMPLERATE
        return temp * self.vol

    def release(self):
        for op in self.ops:
            op.envelope.stage = 4

    def press(self):
        for op in self.ops:
            op.feedback = 0
            op.envelope.stage = 1
            op.envelope.cur = 0
            op.acc_phase = 0
        self.clock = 0


def algtest(ops, clock, size):
    return samples_fb(ops[0], clock, size)


def samples(op, clock, size):
    first = np.sin(np.fromfunction(lambda x: op.sample(clock + (x / SAMPLERATE)), (size,)))
    vol = op.envelope.get_vols(size)
    return np.multiply(vol, np.sin(first))


def samples_with(op, clock, size, in_op):
    first = np.fromfunction(lambda x: op.sample(clock + (x / SAMPLERATE)), (size,))
    vol = op.envelope.get_vols(size)
    s_in = np.multiply(in_op, op.mod)
    return np.multiply(vol, np.sin(np.add(first, s_in)))


def samples_fb(op, clock, size):
    temp = np.empty(size)
    temp[0] = np.sin(op.sample(clock) + (op.mod * op.feedback))
    for i in range(1, size):
        temp[i] = np.sin((op.mod * temp[i - 1]) + op.sample(clock + (i / SAMPLERATE)))
    op.feedback = temp[size - 1]
    tempvols = op.envelope.get_vols(size)
    return np.multiply(temp, tempvols)


def alg1(ops, clock, size):
    first = samples_fb(ops[0], clock, size)
    second = samples_with(ops[1], clock, size, first)
    third = samples_with(ops[2], clock, size, second)
    return samples_with(ops[3], clock, size, third)

def alg2(ops, clock, size):
    first = (samples_fb(ops[0], clock, size) + samples(ops[1], clock, size)) / 2
    second = samples_with(ops[2], clock, size, first)
    return samples_with(ops[3], clock, size, second)

def alg3(ops, clock, size):
    first = samples_fb(ops[0], clock, size)
    second = samples(ops[1], clock, size)
    third = (first + samples_with(ops[2], clock, size, second)) / 2
    return samples_with(ops[3], clock, size, third)

#algs 3 and 4 only differ in where the feedback op gets added
def alg4(ops, clock, size):
    first = samples_fb(ops[0], clock, size)
    second = samples(ops[2], clock, size)
    third = (second + samples_with(ops[1], clock, size, first)) / 2
    return samples_with(ops[3], clock, size, third)

def alg5(ops, clock, size):
    first = samples_fb(ops[0], clock, size)
    second = samples_with(ops[1], clock, size, first)
    third = samples(ops[2], clock, size)
    return (second + samples_with(ops[3], clock, size, third)) / 2

def alg6(ops, clock, size):
    first = samples_fb(ops[0], clock, size)
    second = samples_with(ops[1], clock, size, first)
    third = samples_with(ops[2], clock, size, first)
    fourth = samples_with(ops[3], clock, size, first)
    return (second + third + fourth) / 3

def alg7(ops, clock, size):
    first = samples_fb(ops[0], clock, size)
    second = samples_with(ops[1], clock, size, first)
    return (second + samples(ops[2], clock, size) + samples(ops[3], clock, size)) / 3

def alg8(ops, clock, size):
    first = samples_fb(ops[0], clock, size) + samples(ops[1], clock, size)
    second = samples(ops[2], clock, size) + samples(ops[3], clock, size)
    return (first + second) / 4

alg = {
        0 : alg1,
        1 : alg2,
        2 : alg3,
        3 : alg4,
        4 : alg5,
        5 : alg6,
        6 : alg7,
        7 : alg8,
        8 : algtest
}


def lerp(startval, endval, time, endtime):
    if time > endtime:
        return endval
    else:
        temp = (endval - startval) * (time / endtime)
        return startval + temp
