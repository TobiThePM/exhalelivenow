"""Ẹ ṣé reel score: a warm, sweet lo-fi groove synced to the Remotion timeline.

Rhodes keys + music box + snaps, shaker, soft kick and bass, with Foley-style cues
(paper rustle, record beep, pen scratch, stamp, delivery chime). F major, 120 BPM = 15 frames/beat.
Frame numbers mirror src/index.jsx.
"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve

SR, FPS, FRAMES = 44100, 30, 630
N = int(FRAMES / FPS * SR)
rng = np.random.default_rng(23)
L = np.zeros(N)
R = np.zeros(N)


def at(frame):
    return int(round(frame / FPS * SR))


def add(sig, frame, gain=1.0, pan=0.0):
    i = at(frame)
    if i >= N or i < 0:
        return
    j = min(N, i + len(sig))
    L[i:j] += sig[: j - i] * gain * np.sqrt(0.5 * (1 - pan))
    R[i:j] += sig[: j - i] * gain * np.sqrt(0.5 * (1 + pan))


def tt(sec):
    return np.arange(int(sec * SR)) / SR


def flt(x, kind, hz, order=2):
    return sosfilt(butter(order, hz, kind, fs=SR, output='sos'), x)


def hz(note):
    names = {'C': 0, 'Db': 1, 'D': 2, 'Eb': 3, 'E': 4, 'F': 5, 'Gb': 6, 'G': 7, 'Ab': 8, 'A': 9, 'Bb': 10, 'B': 11}
    return 440 * 2 ** ((names[note[:-1]] + 12 * (int(note[-1]) + 1) - 69) / 12)


def noise(sec):
    return rng.standard_normal(int(sec * SR))


# ---- instruments ----
def rhodes(note, dur=2.2):
    t = tt(dur)
    f = hz(note)
    body = sum(np.sin(2 * np.pi * f * k * t) * np.exp(-t * (1.1 + 0.9 * k)) / k ** 1.6 for k in range(1, 5))
    tine = np.sin(2 * np.pi * f * 7.0 * t) * np.exp(-t * 28) * 0.18
    trem = 1 + 0.12 * np.sin(2 * np.pi * 4.8 * t)
    return flt((body + tine) * trem * np.minimum(1, t / 0.003), 'lowpass', 4500)


def chord(notes, frame, gain, spread=0.6):
    for k, n in enumerate(notes):
        add(rhodes(n), frame + k * 0.25, gain / len(notes) * 1.8, pan=spread * (k / max(1, len(notes) - 1) - 0.5))


def musicbox(note, dur=1.3):
    t = tt(dur)
    f = hz(note)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 4.02 * t) * np.exp(-t * 9)
    return s * np.exp(-t * 3.0) * np.minimum(1, t / 0.002)


def kick():
    t = tt(0.32)
    s = np.sin(2 * np.pi * np.cumsum(48 + 60 * np.exp(-t / 0.03)) / SR) * np.exp(-t / 0.11)
    return flt(s, 'lowpass', 300)


def snap():
    t = tt(0.12)
    s = flt(noise(0.12), 'bandpass', [1400, 3800]) * np.exp(-t / 0.018)
    s += np.sin(2 * np.pi * 1250 * t) * np.exp(-t / 0.01) * 0.4
    return s


def shaker():
    t = tt(0.07)
    return flt(noise(0.07), 'highpass', 6500) * np.sin(np.pi * t / 0.07) ** 2


def bass(note, dur=0.45):
    t = tt(dur)
    f = hz(note)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)
    return flt(s * np.exp(-t / 0.28) * np.minimum(1, t / 0.008), 'lowpass', 700)


def pad(notes, dur):
    t = tt(dur + 1.2)
    s = sum(np.sin(2 * np.pi * hz(n) * (1 + d) * t + rng.uniform(0, 6)) for n in notes for d in (-0.0015, 0, 0.0017))
    env = np.minimum(1, t / 0.9) * np.where(t < dur, 1, np.exp(-(t - dur) / 0.4))
    return flt(s * env, 'lowpass', 1600) / (3 * len(notes))


# ---- Foley ----
def paper(sec=0.6):
    t = tt(sec)
    crackle = (rng.random(len(t)) < 0.02) * rng.standard_normal(len(t)) * 3
    s = flt(noise(sec) * 0.6 + crackle, 'bandpass', [700, 6000])
    return s * np.sin(np.pi * t / sec) ** 2


def beep():
    a = np.sin(2 * np.pi * 880 * tt(0.09)) * np.hanning(int(0.09 * SR))
    b = np.sin(2 * np.pi * 1320 * tt(0.12)) * np.hanning(int(0.12 * SR))
    return np.concatenate([a, np.zeros(int(0.03 * SR)), b])


def pen():
    t = tt(0.045)
    return flt(noise(0.045), 'bandpass', [2500, 6500]) * np.sin(np.pi * t / 0.045)


def stamp():
    t = tt(0.25)
    thud = np.sin(2 * np.pi * np.cumsum(70 + 80 * np.exp(-t / 0.02)) / SR) * np.exp(-t / 0.07)
    return thud + flt(noise(0.25), 'lowpass', 900) * np.exp(-t / 0.03) * 0.7


def seal_drop(note):
    m = musicbox(note, 0.9) * 0.5
    m[: int(0.25 * SR)] += stamp() * 0.6
    return m


def chime(notes=('F5', 'A5', 'C6', 'F6')):
    t = tt(2.2)
    return sum(np.sin(2 * np.pi * hz(n) * t) * np.exp(-t / (1.3 - 0.2 * k)) * np.minimum(1, t / 0.003) for k, n in enumerate(notes)) / 3


def riser(sec):
    t = tt(sec)
    f = 220 * (1760 / 220) ** (t / sec)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4 + flt(noise(sec), 'highpass', 4000) * 0.2) * (t / sec) ** 2.5


def bloom():
    t = tt(3.0)
    s = sum(np.sin(2 * np.pi * hz(n) * t) for n in ('F3', 'C4', 'F4', 'G4', 'A4', 'C5'))
    return flt(s, 'lowpass', 3000) * np.minimum(1, t / 0.015) * np.exp(-t / 1.4) / 4


# ---- harmony: F C Dm Bb, one chord per bar (60 frames) ----
PROG = [
    (['F3', 'A3', 'C4', 'E4'], 'F2'), (['C3', 'E3', 'G3', 'B3'], 'C2'),
    (['D3', 'F3', 'A3', 'C4'], 'D2'), (['Bb2', 'D3', 'F3', 'A3'], 'Bb1'),
]


def bar_of(fr):
    return PROG[(int(fr) // 60) % 4]


# Rhodes: a warm chord every half bar everywhere except the torch hush
for fr in range(0, 630, 30):
    if 450 <= fr < 525:
        continue
    notes, _ = bar_of(fr)
    chord(notes, fr, 0.32 if fr % 60 == 0 else 0.2)

# groove: enters with the first swing, drops for the torch, returns on the end card
for fr in range(75, 615, 15):
    if 450 <= fr < 540:
        continue
    beat = (fr // 15) % 4
    if beat in (0, 2):
        add(kick(), fr, 0.5)
    else:
        add(snap(), fr, 0.32, pan=0.15)
    add(bass(bar_of(fr)[1] if beat != 3 else bar_of(fr)[1][:-1] + str(int(bar_of(fr)[1][-1]) + 1)), fr, 0.33)
for fr in np.arange(75, 615, 7.5):
    if 450 <= fr < 540:
        continue
    add(shaker(), fr + (1.2 if int(fr / 7.5) % 2 else 0), 0.06 if int(fr / 7.5) % 2 else 0.1, pan=-0.3)

# 1. hook: a music-box note blooms under every word
for i, fr in enumerate(range(8, 41, 4)):
    add(musicbox(['C5', 'F5', 'A5', 'G5', 'F5', 'A5', 'C6', 'A5', 'F5'][i]), fr, 0.22, pan=(-0.3 if i % 2 else 0.3))

# 2. pendulum: paper rustle on each swing, a note as each letter lands
for k in range(4):
    add(paper(0.7), 75 + 45 * k + 22.5 - 10, 0.35, pan=(-0.5 if k % 2 == 0 else 0.5))
    add(musicbox(['A5', 'C6', 'D6', 'F6'][k]), 75 + 45 * k + 34, 0.2)

# 3. steps: seal lands on each step, then each step's own sound
for land, note in ((279, 'F5'), (339, 'A5'), (399, 'C6')):
    add(seal_drop(note), land, 0.45)
add(beep(), 293, 0.16)                                  # record
for fr in range(355, 382, 2):                           # pen writes the date
    add(pen(), fr + rng.uniform(-0.3, 0.3), 0.09, pan=0.2)
add(stamp(), 353, 0.4)                                  # postmark pops
add(paper(0.9), 412, 0.22)                              # letter sealing
add(chime(('C6', 'F6')), 439, 0.25)                     # delivered
for i, fr in enumerate(np.arange(255, 450, 15)):        # music-box melody over the groove
    if i % 2 == 0:
        add(musicbox(['A5', 'G5', 'F5', 'G5', 'A5', 'C6', 'A5', 'G5', 'F5', 'E5', 'F5', 'G5', 'A5', 'A5'][i % 14]), fr, 0.1, pan=0.35)

# 4. torch: hush, a pad, a match-strike flicker, a riser into a warm bloom
add(pad(['F3', 'A3', 'C4'], 75 / FPS), 450, 0.35)
add(flt(noise(0.15), 'bandpass', [1500, 7000]) * np.exp(-tt(0.15) / 0.05), 450, 0.25)
for fr in (452, 455, 456):
    add(pen(), fr, 0.2)
add(riser(1.0), 495, 0.35)
add(bloom(), 525, 0.7)
add(chime(), 525, 0.35)

# 5. end card: the seal bounces up the scale, a bell as the button pops
add(paper(0.5), 542, 0.25)
for fr, note, g in ((562, 'C5', 0.5), (576, 'F5', 0.4), (586, 'A5', 0.3)):
    add(seal_drop(note), fr, g)
add(chime(('F5', 'C6', 'F6')), 590, 0.3)
chord(['F3', 'A3', 'C4', 'E4', 'G4'], 600, 0.35)

# ---- master: room reverb, glue, normalise, fade ----
def room(x, seed):
    r = np.random.default_rng(seed)
    t = tt(1.8)
    ir = flt(r.standard_normal(len(t)) * np.exp(-t / 0.4), 'lowpass', 6000)
    ir[0] = 0
    return fftconvolve(x, ir)[: len(x)] / np.sqrt(np.sum(ir ** 2)) * 0.08


mix = np.stack([L + room(L, 1), R + room(R, 2)], axis=1)
mix = flt(mix.T, 'highpass', 30).T
mix = np.tanh(mix * 1.15)
mix *= 10 ** (-1 / 20) / np.max(np.abs(mix))
fade = int(0.7 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
wavfile.write(sys.argv[1], SR, (mix * 32767).astype(np.int16))
print('wrote', sys.argv[1])
