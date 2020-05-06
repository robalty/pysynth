import math
import numpy as np

class ADSR:
    def __init__(self, a=0.1, d=0.2, s=0.6, r=0.1, rtime=0):
        self.a = a
        self.d = d
        self.s = s
        self.r = r
        self.rtime = rtime

    def get_vol(self, clock):
        if self.rtime != 0:
            return lerp(self.s, 0, clock - self.rtime, self.r)
        elif clock < self.a:
            return lerp(0, 1, clock, self.a)
        elif clock < (self.a + self.d):
            return lerp(1, self.s, (clock - self.a), self.d)
        else:
            return self.s

class Operator:
    def __init__(self, i=1, f=220, m=1, env=ADSR()):
        self.modulation = i
        self.frequency = f
        self.freq_mult = m
        self.envelope = env
        self.feedback = 0

    def sample(self, clock):
        vol = self.envelope.get_vol(clock)
        curval = 2 * math.pi * self.frequency * self.freq_mult * clock
        return vol * math.sin(curval)

    def sample_with(self, in_op, clock):
        vol = self.envelope.get_vol(clock)
        curval = 2 * math.pi * self.frequency * self.freq_mult * clock
        return vol * math.sin(curval + (self.modulation * in_op))
    
    def sample_fb(self, clock):
        temp = self.sample_with(self.feedback, clock)
        self.feedback = temp
        return temp

class Synth:
    def __init__(self):
        self.ops = [Operator(), Operator(), Operator(), Operator()]
        self.algorithm = 1
        self.clock = 0.0
        self.samplerate = 48000
        self.frequency = 220
        self.vol = 0

    def set_freq(self, val):
        self.frequency = val
        for i in self.ops:
            i.frequency = val

    def get_sample(self):
        func = alg.get(self.algorithm)
        return self.vol * func(self.ops, self.clock)

    def step(self):
        self.clock += 1/self.samplerate

    def get_samples(self, num_samples):
        temp = np.empty(num_samples, dtype=np.int16)
        func = alg.get(self.algorithm)
        for i in range(0, num_samples):
            np.put(temp, i, self.vol * func(self.ops, self.clock))
            self.clock += 1/self.samplerate
        return temp

    def release(self):
        for op in self.ops:
            op.envelope.rtime = self.clock

    def press(self):
        self.clock = 0
        for op in self.ops:
            op.envelope.rtime = 0


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
