import math

class ADSR:
    def __init__(self, a=0, d=0.1, s=0.7, r=0.1, rtime=0):
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

    def get_sample(self, in_op, clock):
        vol = self.envelope.get_vol(clock)
        curval = 2 * math.pi * self.frequency * self.freq_mult * clock
        return vol * math.sin(curval + (self.modulation * in_op))

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

    def set_vol(self, val):
        self.vol = val

    def get_sample(self):
        func = alg.get(self.algorithm)
        return (self.vol / 127) * func(self.ops, self.clock)

    def step(self):
        self.clock += 1/self.samplerate

    def get_samples(self, num_samples):
        temp = []
        for i in range(0, num_samples):
            temp.append(self.get_sample())
            self.step()
        return temp

    def release(self):
        for op in self.ops:
            op.envelope.rtime = self.clock

    def press(self):
        self.clock = 0
        for op in self.ops:
            op.envelope.rtime = 0


def algtest(ops, clock):
    return ops[0].get_sample(0, clock)
def alg1(ops, clock):
    first = ops[0].get_sample(0, clock)
    second = ops[1].get_sample(first, clock)
    third = ops[2].get_sample(second, clock)
    return ops[2].get_sample(third, clock)
def alg2(ops, clock):
    return ops[0].get_sample(0, clock)
def alg3(ops, clock):
    return ops[0].get_sample(0, clock)

alg = {
        0 : algtest,
        1 : alg1,
        2 : alg2,
        3 : alg3
}

def lerp(startval, endval, time, endtime):
    if time > endtime:
        return endval
    else:
        temp = (endval - startval) * (time / endtime)
        return startval + temp
