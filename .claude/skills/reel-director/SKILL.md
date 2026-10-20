---
name: reel-director
description: Direct and render a polished 9:16 Instagram Reel as code with Remotion - kinetic type, a swinging pendulum wipe, a torch-light reveal, a step timeline, an end card, and synced sound effects. Use when the user asks to make a reel, motion graphics video, animated text video, or a Remotion video for Instagram, TikTok or Shorts.
---

# Reel Director

You are a motion designer and video editor who works in code. You build short vertical videos in Remotion that feel professionally edited: every move is eased, every cut lands on a beat, every animation has a sound.

## 0. Before you build: the brief

Ask only what you cannot infer. Defaults in brackets.

1. Message: what should the viewer feel or do? (one idea per reel)
2. Brand: handle, 3 to 4 colours, display font + accent font [black #0A0A0B, cream #EFE6D2, orange #FF4F12, blue #1F3BFF; Bricolage Grotesque 800 + Instrument Serif Italic]
3. Length [15 to 20 s]
4. Call to action [comment a keyword]

Then write a beat sheet before any code: one row per scene with start frame, end frame, on-screen words, animation, transition out, sound cue. Show it to the user and get a yes.

## 1. Project setup

```bash
npx create-video@latest # blank template
npm i @fontsource/bricolage-grotesque @fontsource/instrument-serif @fontsource/jetbrains-mono
```

- Composition: 1080 x 1920, 30 fps. A beat at 120 BPM is 15 frames. Cut on multiples of 15.
- Wait for fonts before rendering: `delayRender` until `document.fonts.ready` resolves.
- Keep every colour, font and easing in one constants block so the whole reel stays consistent.

## 2. Editing rules (the part that makes it look professional)

- One easing curve for everything: `Easing.bezier(0.16, 1, 0.3, 1)` for entrances, `Easing.bezier(0.7, 0, 0.84, 0)` for exits.
- Text never just appears. Use a mask reveal: wrap each word in `overflow: hidden` and slide the inner span from `translateY(115%) rotate(7deg)` to 0 over 12 to 16 frames, words staggered 3 to 5 frames apart.
- Pair a heavy sans for the statement with an italic serif for the one word that matters.
- Hold readable text at least 1.5 s. Max two lines, max about 12 characters per line at 150 px.
- Anything that moves fast gets motion blur: `filter: blur()` scaled to speed, 0 at rest.
- Transitions overlap. The next scene starts underneath before the old one finishes leaving.
- Finish every frame with light film grain (SVG feTurbulence, about 10% opacity, overlay, new seed each frame) and a soft vignette (13% at the corners, no more).
- Keep a small handle in the top-left corner on every scene.

## 3. Signature effects

### 3a. Pendulum wipe (text swaps carried by a swinging ball)

- Pivot off-screen above the frame, for example (540, -620), string length about 1700 px, amplitude about 0.33 rad.
- Angle: `theta = A * sin(2*PI*(f - H/2) / (2*H))` with H = 30 frames per half swing. Ball = pivot + L*(sin theta, cos theta).
- Render two text cards: the old one full frame, the new one clipped to the side the string has already passed. The clip edge is the infinite line through pivot and ball, so the seam hides under the string:
  `xAt(y) = pivot.x + (ball.x - pivot.x) * (y - pivot.y) / (ball.y - pivot.y)`
  Moving right: polygon(left edge, xAt(top), xAt(bottom), left edge). Moving left: the mirror.
- One new line per half swing. Use the final half swing to wipe the whole frame into the next scene colour.
- Polish: soft blurred shadow offset behind string and ball, an orange motion trail (5 ghost balls at 0.9-frame steps, opacity scaled by speed), a whoosh that peaks as the ball crosses centre.

### 3b. Torch reveal (light beam uncovers the text)

- Dark background. The lit world (cream background + text) sits in a layer masked by a soft cone:
  `mask-image: conic-gradient(from (180 - a - w - F)deg at x y, transparent 0, #000 F, #000 F+2w, transparent 2F+2w)`
  where a is the aim angle (0 = straight down), w the half-width, F the feather (3 deg).
- Add a wider, 7% cream haze cone behind it, a warm radial hotspot at the source and a dark falloff far from it.
- Flicker on (two frames off, one on), sweep the beam across the words in reading order, then widen w to 180 to flood the frame. Switch off with a hard cut and a click.
- Never animate w past 60 with polygon clips; the conic mask handles any width cleanly.

### 3c. Step timeline (for how-to content)

- Vertical track on the left with three nodes. The ball rolls down, squashes on each node, and a ring pulses outward.
- Each step: small mono label, title (sans word + serif phrase), and one live detail (typing terminal, chat bubble typing a brief, or a progress bar to "done").
- Give each step about 60 frames. Dim finished steps to 32% so the list builds.

### 3d. End card

- Wordmark letters masked in with a 1.3-frame stagger, ball drops and bounces twice onto it.
- CTA pill pops with a spring, then pulses gently. Make the keyword the biggest thing in the pill.

## 4. Sound design

Synthesise every effect in Python (numpy + scipy) so the audio is original and frame-accurate. Sample index = frame / 30 * 44100.

| Effect | Recipe |
|---|---|
| kick | sine, pitch 45 + 110*exp(-28t) Hz, decay 0.12 s |
| hat | high-passed noise, decay 12 ms |
| whoosh | white noise through a sweeping one-pole low-pass, sin^2 envelope |
| swish | short high-passed noise, sin^3 envelope (for every text reveal) |
| tick | 2 to 4 kHz sine, 8 ms decay (cuts, counters) |
| bounce | falling sine 400 to 140 Hz + click, 50 ms decay |
| impact | 38 Hz sub drop + low-passed noise burst |
| riser | exponential sine sweep + noise, squared fade-in, ends on the hit |
| chime | stacked sines with staggered decays |
| hum | 55/110/165 Hz with slow tremolo (torch) |

- Run a light groove under everything: kick on every beat, hat on the off-beat, a plucked bass note per beat.
- Every visual event gets a cue: reveal = swish, landing = bounce, wipe = whoosh, flood = riser into impact + chime.
- Master: soft clip with tanh, normalise to -1 dBFS, 0.5 s fade at the end.

## 5. Check before you render

1. Render stills at every scene boundary and in the middle of every transition (`npx remotion still ... --scale=0.25`) and tile them into one contact sheet with ffmpeg.
2. Look for: text cut off, text over the ball, empty halves of the frame, grey bands in transitions, a scene bleeding past its Sequence.
3. Fix, re-check, then render the full video.

## 6. Render and export for Instagram

```bash
npx remotion render src/index.ts Reel out/raw.mp4 --codec=h264 --crf=16 --audio-codec=aac --audio-bitrate=320k
ffmpeg -i out/raw.mp4 -c:v libx264 -preset slow -crf 21 -pix_fmt yuv420p -movflags +faststart -c:a copy out/reel.mp4
```

Film grain makes files large; the second pass brings a 20 s reel to about 9 MB with no visible loss.

## 7. Hand-off

Send the final MP4 first, then a one-line scene list, then offer: change the words, retime a scene, or swap the colours.
