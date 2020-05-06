import math
import numpy as np

SAMPLERATE = 48000

SINETABLE = np.sin(2 * np.pi * np.arange(0, 1, 1/48000))


class ADSR:
    def __init__(self, a=0.1, d1=0.3, d2=1, s=0.6, r=0.1, rtime=0):
        self.timings = {
                0 : 0,
                1 : 1 / (4 * a * SAMPLERATE),
                2 : -1 / (4 * d1 * SAMPLERATE),
                3 : -1 / (4 * d2 * SAMPLERATE),
                4 : -1 / (4 * r * SAMPLERATE)
        }
        self.s = s
        self.stage = 0
        self.cur = 0

    def get_vol(self):
        if self.stage == 0:
            return 0
        temp = self.cur
        self.cur += self.timings.get(self.stage)
        if self.cur > 1:
            self.cur = 1
            self.stage = 2
        elif (self.stage == 2) & (self.cur < self.s):
            self.stage = 3
        elif (self.cur < 0):
            self.cur = 0
            self.stage = 0
        return temp

class Operator:
    def __init__(self, i=SAMPLERATE, f=220, m=1):
        self.modulation = i / (2 * math.pi)
        self.frequency = f
        self.freq_mult = m
        self.envelope = ADSR()
        self.feedback = 0
        self.acc_phase = 0

    def sample(self, clock):
        vol = self.envelope.get_vol()
        cur = int((self.frequency * clock) + self.acc_phase) % SAMPLERATE
        return vol * SINETABLE[cur]

    def sample_with(self, in_op, clock):
        vol = self.envelope.get_vol()
        cur = int((self.frequency * clock) + (in_op * self.modulation) + self.acc_phase) % SAMPLERATE
        return vol * SINETABLE[cur]
    
    def sample_fb(self, clock):
        vol = self.envelope.get_vol()
        cur = int((self.frequency * clock) + (self.feedback * self.modulation) + self.acc_phase) % SAMPLERATE
        ret = vol * SINETABLE[cur]
        self.feedback = ret
        return ret

class Synth:
    def __init__(self):
        self.ops = [Operator(), Operator(), Operator(), Operator()]
        self.algorithm = 1
        self.clock = 0
        self.samplerate = SAMPLERATE
        self.frequency = 220
        self.vol = 0

    def set_freq(self, val):
        self.frequency = val
        for i in self.ops:
            t = val * i.freq_mult
            i.acc_phase += ((i.frequency - t) * (self.clock)) % SAMPLERATE
            i.frequency = t


    def get_sample(self):
        func = alg.get(self.algorithm)
        return self.vol * func(self.ops, self.clock)

    def step(self):
        self.clock += 1

    def get_samples(self, num_samples):
        func = alg.get(self.algorithm)
        iterable = (self.vol * func(self.ops, x) for x in range(self.clock, self.clock+num_samples))
        temp = np.fromiter(iterable, np.float32, num_samples)
        self.clock += num_samples
        self.clock = self.clock % SAMPLERATE
        return temp

    def release(self):
        for op in self.ops:
            op.envelope.stage = 4

    def press(self):
        self.clock = 0
        for op in self.ops:
            op.envelope.stage = 1
            op.envelope.cur = 0
            op.acc_phase = 0


def algtest(ops, clock):
    return ops[0].sample_fb(clock)
def alg1(ops, clock):
    first = ops[0].sample_fb(clock)
    second = ops[1].sample_with(first, clock)
    third = ops[2].sample_with(second, clock)
    return ops[2].sample_with(third, clock)
def alg2(ops, clock):
    first = ops[0].sample_fb(clock) + ops[1].sample(clock)
    second = ops[2].sample_with(first, clock)
    return ops[3].sample_with(second, clock)
def alg3(ops, clock):
    first = ops[0].sample_fb(clock)
    second = ops[1].sample(clock)
    third = ops[2].sample_with(second, clock)
    return ops[3].sample_with((first + third) / 2, clock)
#alg4 is the same as alg3 except with (0 + 1) + 2 instead of 0 + (1 + 2)
#this makes a difference because operator 0 can have feedback
def alg4(ops, clock):
    first = ops[0].sample_fb(clock)
    second = ops[1].sample_with(first, clock)
    third = ops[2].sample(clock)
    return ops[3].sample_with((second + third) / 2, clock)
def alg5(ops, clock):
    first = ops[0].sample_fb(clock)
    second = ops[1].sample_with(first, clock)
    third = ops[2].sample(clock)
    return (ops[3].sample_with(third, clock) + second) / 2
def alg6(ops, clock):
    first = ops[0].sample_fb(clock)
    return (ops[1].sample_with(first, clock) + ops[2].sample_with(first, clock) + ops[3].sample_with(first, clock)) / 3
def alg7(ops, clock):
    first = ops[0].sample_fb(clock)
    return (ops[1].sample_with(first, clock) + ops[2].sample(clock) + ops[3].sample(clock)) / 3
def alg8(ops, clock):
    return (ops[0].sample_fb(clock) + ops[1].sample(clock) + ops[2].sample(clock) + ops[3].sample(clock)) / 4


alg = {
        0 : algtest,
        1 : alg1,
        2 : alg2,
        3 : alg3,
        4 : alg4,
        5 : alg5,
        6 : alg6,
        7 : alg7,
        8 : alg8
}

def lerp(startval, endval, time, endtime):
    if time > endtime:
        return endval
    else:
        temp = (endval - startval) * (time / endtime)
        return startval + temp
