import React, {useEffect, useState} from 'react';
import {
  AbsoluteFill, Audio, Composition, Easing, continueRender, delayRender,
  interpolate, registerRoot, spring, staticFile, useCurrentFrame,
} from 'remotion';
import '@fontsource/fraunces/400.css';
import '@fontsource/fraunces/400-italic.css';
import '@fontsource/fraunces/500.css';
import '@fontsource/caveat/500.css';
import '@fontsource/caveat/700.css';

// ---------- constants: Ẹ ṣé brand (from the live app's stylesheet) ----------
const C = {
  paper: '#FFFFFF', ink: '#111111', red: '#D7263D', seal: '#A3201B', muted: '#767676', rule: '#E4E4E4',
  cream: '#FBF6EA', photo: '#E8DCC4', air: '#EEF4FB', airEdge: '#9FB8D6', airBlue: '#2A5AA0', keep: '#F6F1F1',
  night: '#14110F',
};
const SERIF = "'Fraunces', Georgia, serif";
const HAND = "'Caveat', cursive";
const IN = Easing.bezier(0.16, 1, 0.3, 1);
const OUT = Easing.bezier(0.7, 0, 0.84, 0);
const W = 1080, H = 1920, FPS = 30, DURATION = 630;
const CL = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'};
const T = {hook: 0, swing: 75, steps: 255, torch: 450, end: 540};
const lerp = (a, b, p) => a + (b - a) * p;
const clamp01 = (x) => Math.min(1, Math.max(0, x));

const italic = {fontFamily: SERIF, fontStyle: 'italic', fontWeight: 400, letterSpacing: '-0.01em'};
const hand = {fontFamily: HAND, fontWeight: 700, color: C.red};

// ---------- masked word reveal ----------
const Word = ({f, start, children, style, dur = 14, gap = '0.12em'}) => {
  const p = interpolate(f - start, [0, dur], [0, 1], {...CL, easing: IN});
  return (
    <span style={{display: 'inline-block', overflow: 'hidden', verticalAlign: 'bottom', paddingBottom: 10}}>
      <span style={{display: 'inline-block', transformOrigin: 'left bottom', padding: `0.04em ${gap} 0.14em`,
        transform: `translateY(${(1 - p) * 115}%) rotate(${(1 - p) * 7}deg)`, ...style}}>{children}</span>
    </span>
  );
};

const Lines = ({f, lines, start, stagger = 4, base, accent, align = 'center'}) => {
  let i = 0;
  return (
    <div style={{textAlign: align}}>
      {lines.map((line, li) => (
        <div key={li} style={{lineHeight: 0.95, whiteSpace: 'nowrap'}}>
          {line.map((w, wi) => (
            <Word key={wi} f={f} start={start + stagger * i++} style={{...(w.hand ? {...hand, ...accent} : base), ...w.style}}>{w.t}</Word>
          ))}
        </div>
      ))}
    </div>
  );
};

const Small = ({children, color = C.muted, style}) => (
  <div style={{fontFamily: SERIF, fontSize: 28, letterSpacing: '0.16em', textTransform: 'uppercase', color, ...style}}>{children}</div>
);

const Center = ({bg, children}) => (
  <AbsoluteFill style={{background: bg, justifyContent: 'center', alignItems: 'center'}}>{children}</AbsoluteFill>
);

// ---------- 1. hook ----------
const HookCard = ({f}) => (
  <Center bg={C.paper}>
    <Lines
      f={f} start={8}
      base={{...italic, fontSize: 138, color: C.ink}}
      accent={{fontSize: 230}}
      lines={[[{t: 'Who'}, {t: 'made'}], [{t: 'this'}, {t: 'year'}], [{t: 'easier', hand: true}], [{t: 'for'}, {t: 'you?'}]]}
    />
  </Center>
);

// ---------- 2. pendulum through the three letter papers ----------
const Letter = ({bg, text, sign, children, edge}) => (
  <AbsoluteFill style={{background: bg}}>
    {edge}
    <div style={{position: 'absolute', left: 110, width: 860, top: 330}}>
      <Small style={{marginBottom: 40}}>{sign}</Small>
      <div style={{fontFamily: HAND, fontWeight: 500, fontSize: 118, lineHeight: 1.02, color: C.ink}}>{text}</div>
      <div style={{fontFamily: HAND, fontWeight: 500, fontSize: 64, color: C.red, marginTop: 24}}>— with love</div>
    </div>
    <div style={{position: 'absolute', left: 110, top: 1300}}>{children}</div>
  </AbsoluteFill>
);

const airStripe = (top) => (
  <div style={{position: 'absolute', left: 0, right: 0, [top ? 'top' : 'bottom']: 0, height: 34,
    background: `repeating-linear-gradient(-45deg, ${C.red} 0 34px, #fff 34px 56px, ${C.airBlue} 56px 90px, #fff 90px 112px)`}} />
);

const CARDS = [
  ({f}) => <HookCard f={f} />,
  () => (
    <Letter bg={C.cream} sign="Plain letter · to Mama" text="Mama, thank you for every early morning.">
      <div style={{width: 300, height: 190, background: C.photo, borderRadius: 8, marginTop: 50, transform: 'rotate(-3deg)', boxShadow: '0 10px 30px rgba(0,0,0,0.08)'}} />
    </Letter>
  ),
  () => (
    <Letter bg={C.air} sign="Airmail · to Tunde" text="Tunde, I never said it properly, so here it is." edge={<>{airStripe(true)}{airStripe(false)}</>} />
  ),
  () => (
    <Letter bg={C.keep} sign="Keepsake · to Mrs. Okafor" text="Mrs. Okafor, you saw me before anyone did.">
      <div style={{width: 120, height: 120, borderRadius: '50%', background: `radial-gradient(circle at 35% 30%, #c8403a, ${C.seal} 70%)`, marginTop: 50, boxShadow: 'inset 0 0 0 8px rgba(255,255,255,0.18)'}} />
    </Letter>
  ),
  () => <AbsoluteFill style={{background: C.paper}} />,
];

const PIV = {x: 540, y: -620}, LEN = 1700, AMP = 0.78, HS = 45, SWINGS = 4, R = 68;
const thetaAt = (f) => {
  const local = Math.min(Math.max(f - T.swing, 0), SWINGS * HS);
  return AMP * Math.sin((Math.PI * (local - HS / 2)) / HS);
};
const ballAt = (f) => {
  const th = thetaAt(f);
  return {x: PIV.x + LEN * Math.sin(th), y: PIV.y + LEN * Math.cos(th)};
};
const xAt = (b, y) => PIV.x + ((b.x - PIV.x) * (y - PIV.y)) / (b.y - PIV.y);

const SealBall = ({x, y, r, blur = 0, sx = 1, sy = 1}) => (
  <g transform={`translate(${x},${y}) scale(${sx},${sy})`} style={{filter: `blur(${blur.toFixed(2)}px)`}}>
    <circle r={r} fill="url(#sealg)" />
    <circle r={r * 0.72} fill="none" stroke="rgba(255,255,255,0.28)" strokeWidth={r * 0.07} />
    <text textAnchor="middle" dy={r * 0.3} fontFamily={SERIF} fontStyle="italic" fontSize={r * 0.95} fill="rgba(255,255,255,0.85)">ẹ</text>
  </g>
);

const SealDefs = () => (
  <defs>
    <filter id="sh" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="12" /></filter>
    <radialGradient id="sealg" cx="35%" cy="30%" r="75%">
      <stop offset="0" stopColor="#E85A5A" />
      <stop offset="0.5" stopColor={C.red} />
      <stop offset="1" stopColor={C.seal} />
    </radialGradient>
  </defs>
);

const Pendulum = ({f}) => {
  const local = f - T.swing;
  let layers;
  if (local < 0) layers = [<HookCard key="0" f={f} />];
  else if (local >= SWINGS * HS) layers = [React.createElement(CARDS[4], {key: '4', f})];
  else {
    const k = Math.floor(local / HS);
    const b = ballAt(f);
    const xt = xAt(b, 0), xb = xAt(b, H);
    const edge = k % 2 === 0 ? 0 : W;
    const clip = `polygon(${edge}px 0px, ${xt}px 0px, ${xb}px ${H}px, ${edge}px ${H}px)`;
    layers = [
      React.createElement(CARDS[k], {key: 'old', f}),
      <AbsoluteFill key="new" style={{clipPath: clip}}>{React.createElement(CARDS[k + 1], {f})}</AbsoluteFill>,
    ];
  }
  const b = ballAt(f);
  const prev = ballAt(f - 1);
  const speed = Math.hypot(b.x - prev.x, b.y - prev.y);
  const sp = clamp01(speed / 70);
  const show = local >= 0 && local <= SWINGS * HS;
  return (
    <AbsoluteFill>
      {layers}
      {show && (
        <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
          <SealDefs />
          <g transform="translate(22,30)" opacity={0.22} filter="url(#sh)">
            <line x1={PIV.x} y1={PIV.y} x2={b.x} y2={b.y} stroke="#000" strokeWidth={5} />
            <circle cx={b.x} cy={b.y} r={R} fill="#000" />
          </g>
          {[1, 2, 3, 4, 5].map((i) => {
            const g = ballAt(f - 0.9 * i);
            return <circle key={i} cx={g.x} cy={g.y} r={R * (1 - i * 0.06)} fill={C.red} opacity={Math.max(0, (0.3 - i * 0.05) * sp)} />;
          })}
          <line x1={PIV.x} y1={PIV.y} x2={b.x} y2={b.y} stroke={C.ink} strokeWidth={3} />
          <SealBall x={b.x} y={b.y} r={R} blur={speed * 0.09} />
        </svg>
      )}
    </AbsoluteFill>
  );
};

// ---------- 3. how it works: step timeline ----------
const NODES = [690, 1050, 1410];
const LANDS = [24, 84, 144];
const TRACK_X = 140;
const stepBallY = (t) => {
  if (t < 10) return -150;
  if (t < 24) return lerp(-150, NODES[0], ((t - 10) / 14) ** 2);
  if (t < 70) return NODES[0];
  if (t < 84) return lerp(NODES[0], NODES[1], OUT((t - 70) / 14));
  if (t < 130) return NODES[1];
  if (t < 144) return lerp(NODES[1], NODES[2], OUT((t - 130) / 14));
  return NODES[2];
};
const typed = (s, t, start, cps) => s.slice(0, Math.max(0, Math.min(s.length, Math.floor((t - start) * cps))));

const Step = ({t, i, label, word, phrase, detail}) => {
  const land = LANDS[i];
  const next = LANDS[i + 1];
  const dim = next === undefined ? 1 : interpolate(t, [next, next + 8], [1, 0.32], CL);
  return (
    <div style={{position: 'absolute', left: 230, top: NODES[i] - 34, width: 800, opacity: dim}}>
      <div style={{opacity: interpolate(t - land, [0, 8], [0, 1], CL)}}><Small color={C.red} style={{fontSize: 24}}>{label}</Small></div>
      <div style={{marginTop: 4, marginLeft: -10}}>
        <Lines f={t} start={land + 2} align="left"
          base={{fontFamily: SERIF, fontWeight: 500, fontSize: 96, color: C.ink, letterSpacing: '-0.03em'}}
          accent={{fontSize: 92}}
          lines={[[{t: word}], [{t: phrase, hand: true}]]} />
      </div>
      <div style={{marginTop: 10}}>{detail(t - land)}</div>
    </div>
  );
};

const RecordDetail = (dt) => {
  const on = dt >= 14;
  const secs = Math.max(0, Math.min(12, Math.floor((dt - 16) / 3)));
  return (
    <div style={{display: 'flex', alignItems: 'center', gap: 22, opacity: on ? 1 : 0}}>
      <div style={{width: 50, height: 50, borderRadius: '50%', background: C.red, opacity: 0.55 + 0.45 * Math.abs(Math.sin(dt / 5)), boxShadow: `0 0 0 6px #fff, 0 0 0 8px ${C.red}`}} />
      <div style={{display: 'flex', alignItems: 'center', gap: 5, height: 56}}>
        {Array.from({length: 26}, (_, k) => {
          const active = k < (dt - 16) * 0.9;
          const h = 8 + 40 * Math.abs(Math.sin(k * 1.7 + dt * 0.35) * Math.cos(k * 0.6));
          return <span key={k} style={{width: 6, height: active ? h : 8, borderRadius: 3, background: active ? C.ink : '#C9C9C9'}} />;
        })}
      </div>
      <div style={{fontFamily: SERIF, fontSize: 34, color: C.ink, fontVariantNumeric: 'tabular-nums'}}>0:{String(secs).padStart(2, '0')}</div>
    </div>
  );
};

const PostmarkDetail = (dt) => {
  const pop = spring({frame: dt - 14, fps: FPS, config: {damping: 13, stiffness: 180}});
  const s = 'Christmas morning · 25 Dec';
  return (
    <div style={{display: 'inline-block', transform: `scale(${pop}) rotate(-2deg)`, transformOrigin: 'left center', border: `3px solid ${C.red}`, borderRadius: 999, padding: '12px 30px', color: C.red, ...italic, fontSize: 38}}>
      {typed(s, dt, 18, 1.1)}<span style={{opacity: dt % 16 < 8 ? 1 : 0}}>|</span>
    </div>
  );
};

const DeliverDetail = (dt) => {
  const p = interpolate(dt, [14, 40], [0, 1], {...CL, easing: IN});
  const done = dt >= 40;
  return (
    <div style={{display: 'flex', alignItems: 'center', gap: 24, opacity: interpolate(dt, [10, 16], [0, 1], CL)}}>
      <div style={{width: 300, height: 8, background: C.rule}}>
        <div style={{width: `${p * 100}%`, height: '100%', background: C.ink}} />
      </div>
      <div style={{...italic, fontSize: 36, color: done ? C.red : C.ink, whiteSpace: 'nowrap'}}>{done ? 'delivered ✓' : 'sealing…'}</div>
    </div>
  );
};

const Steps = ({f}) => {
  const t = f - T.steps;
  const y = stepBallY(t);
  const vy = Math.abs(y - stepBallY(t - 1));
  const lastLand = [...LANDS].reverse().find((l) => t >= l);
  let sy = 1 + Math.min(vy * 0.004, 0.25);
  if (lastLand !== undefined && t - lastLand < 12) sy = interpolate(t - lastLand, [0, 2, 6, 11], [0.62, 1.12, 0.96, 1], CL);
  const sx = 1 / Math.sqrt(sy);
  const r = 36;
  return (
    <AbsoluteFill style={{background: C.paper}}>
      <div style={{position: 'absolute', top: 280, left: 80, right: 80}}>
        <div style={{opacity: interpolate(t, [0, 8], [0, 1], CL)}}><Small>How it works</Small></div>
        <div style={{marginTop: 10, marginLeft: -12}}>
          <Lines f={t} start={3} align="left" base={{...italic, fontSize: 112, color: C.ink}} accent={{fontSize: 130}}
            lines={[[{t: 'Three'}, {t: 'little'}, {t: 'steps', hand: true}]]} />
        </div>
      </div>
      <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
        <SealDefs />
        <line x1={TRACK_X} y1={NODES[0]} x2={TRACK_X} y2={NODES[2]} stroke={C.rule} strokeWidth={4} strokeDasharray="2 14" strokeLinecap="round" opacity={interpolate(t, [4, 14], [0, 1], CL)} />
        {t >= LANDS[0] && <line x1={TRACK_X} y1={NODES[0]} x2={TRACK_X} y2={y} stroke={C.ink} strokeWidth={3} />}
        {NODES.map((n, i) => (
          <circle key={i} cx={TRACK_X} cy={n} r={14} fill={t >= LANDS[i] ? C.ink : C.paper} stroke={C.ink} strokeWidth={3} opacity={interpolate(t, [4 + i * 3, 14 + i * 3], [0, 1], CL)} />
        ))}
        {LANDS.map((l, i) => {
          const dt = t - l;
          if (dt < 0 || dt > 24) return null;
          return <circle key={i} cx={TRACK_X} cy={NODES[i]} r={interpolate(dt, [0, 24], [r, 140], {...CL, easing: IN})} fill="none" stroke={C.red} strokeWidth={3} opacity={interpolate(dt, [0, 24], [0.6, 0], CL)} />;
        })}
        <SealBall x={TRACK_X} y={y + r - r * sy} r={r} sx={sx} sy={sy} blur={Math.min(vy * 0.1, 6)} />
      </svg>
      <Step t={t} i={0} label="01 · Record" word="Say it" phrase="in your own words" detail={RecordDetail} />
      <Step t={t} i={1} label="02 · Schedule" word="Pick" phrase="the perfect day" detail={PostmarkDetail} />
      <Step t={t} i={2} label="03 · Deliver" word="We send it" phrase="on paper they'll keep" detail={DeliverDetail} />
    </AbsoluteFill>
  );
};

// ---------- 4. torch reveal ----------
const SRC = {x: 70, y: 250};
const aimAt = (x, y) => (Math.atan2(x - SRC.x, y - SRC.y) * 180) / Math.PI;
const Torch = ({f}) => {
  const t = f - T.torch;
  const on = t >= 6 || t === 2 || t === 5;
  const a = interpolate(t, [6, 50], [aimAt(540, 680) + 6, aimAt(540, 1260) - 4], {...CL, easing: Easing.inOut(Easing.sin)});
  const w = interpolate(t, [50, 75], [13, 180], {...CL, easing: Easing.in(Easing.cubic)});
  const F = 3;
  const cone = (ww, col, col0) => `conic-gradient(from ${180 - a - ww - F}deg at ${SRC.x}px ${SRC.y}px, ${col0} 0deg, ${col} ${F}deg, ${col} ${F + 2 * ww}deg, ${col0} ${2 * F + 2 * ww}deg)`;
  const mask = cone(w, '#000', 'transparent');
  const flood = interpolate(t, [50, 75], [0, 1], CL);
  return (
    <AbsoluteFill style={{background: C.night}}>
      {on && (
        <>
          <AbsoluteFill style={{background: cone(Math.min(w * 1.7, 180), 'rgba(255,248,235,0.07)', 'rgba(255,248,235,0)')}} />
          <AbsoluteFill style={{maskImage: mask, WebkitMaskImage: mask}}>
            <AbsoluteFill style={{background: C.cream, justifyContent: 'center', alignItems: 'center'}}>
              <div style={{textAlign: 'center'}}>
                <div style={{...italic, fontSize: 140, color: C.ink, lineHeight: 1}}>Some words</div>
                <div style={{...italic, fontSize: 140, color: C.ink, lineHeight: 1.05}}>deserve to be</div>
                <div style={{...hand, fontSize: 300, lineHeight: 1}}>kept.</div>
              </div>
            </AbsoluteFill>
            <AbsoluteFill style={{opacity: 1 - flood, background: `radial-gradient(circle at ${SRC.x}px ${SRC.y}px, rgba(20,17,15,0) 700px, rgba(20,17,15,0.6) 1700px)`}} />
          </AbsoluteFill>
          <AbsoluteFill style={{opacity: 1 - flood * 0.8, background: `radial-gradient(circle at ${SRC.x}px ${SRC.y}px, rgba(255,238,205,0.85) 0px, rgba(255,226,180,0.35) 70px, rgba(255,226,180,0) 220px)`}} />
        </>
      )}
    </AbsoluteFill>
  );
};

// ---------- 5. end card ----------
const END_LANDS = [22, 36, 46];
const endBallY = (t, floor) => {
  if (t < 10) return -200;
  if (t < 22) return lerp(-200, floor, ((t - 10) / 12) ** 2);
  const hop = (t0, t1, h) => { const p = (t - t0) / (t1 - t0); return floor - h * 4 * p * (1 - p); };
  if (t < 36) return hop(22, 36, 230);
  if (t < 46) return hop(36, 46, 80);
  return floor;
};
const EndCard = ({f}) => {
  const t = f - T.end;
  const R2 = 42, floor = 515;
  const y = endBallY(t, floor);
  const vy = Math.abs(y - endBallY(t - 1, floor));
  const last = [...END_LANDS].reverse().find((l) => t >= l);
  let sy = 1 + Math.min(vy * 0.004, 0.25);
  if (last !== undefined && t - last < 10) sy = interpolate(t - last, [0, 2, 5, 9], [0.65, 1.1, 0.97, 1], CL);
  const sx = 1 / Math.sqrt(sy);
  const pop = spring({frame: t - 50, fps: FPS, config: {damping: 11, stiffness: 160}});
  const pulse = t > 66 ? 1 + 0.025 * Math.sin(((t - 66) / 30) * Math.PI * 2) : 1;
  return (
    <AbsoluteFill style={{background: C.paper}}>
      <div style={{position: 'absolute', top: 520, left: 0, right: 0, textAlign: 'center', ...italic, fontSize: 300, color: C.ink, lineHeight: 1}}>
        {'Ẹ ṣé'.split('').map((ch, i) => <Word key={i} f={t} start={4 + i * 1.3} dur={12} gap="0.02em">{ch === ' ' ? ' ' : ch}</Word>)}
      </div>
      <div style={{position: 'absolute', top: 880, left: 0, right: 0, textAlign: 'center', opacity: interpolate(t, [16, 26], [0, 1], CL)}}>
        <div style={{fontFamily: SERIF, fontSize: 36, color: C.muted, letterSpacing: '0.06em'}}>eh-sheh · thank you</div>
      </div>
      <div style={{position: 'absolute', top: 980, left: 0, right: 0}}>
        <Lines f={t} start={24} stagger={3} base={{...hand, fontSize: 76}} lines={[[{t: 'your'}, {t: 'voice,'}, {t: 'on'}, {t: 'paper'}], [{t: "they'll"}, {t: 'keep'}]]} />
      </div>
      <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
        <SealDefs />
        <SealBall x={672} y={y + R2 - R2 * sy} r={R2} sx={sx} sy={sy} blur={Math.min(vy * 0.08, 6)} />
      </svg>
      <div style={{position: 'absolute', top: 1290, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
        <div style={{transform: `scale(${pop * pulse})`, background: C.ink, color: C.paper, padding: '28px 70px', display: 'flex', alignItems: 'baseline', gap: 24, boxShadow: '0 20px 50px rgba(0,0,0,0.18)'}}>
          <span style={{...italic, fontSize: 48}}>Start</span>
          <span style={{fontFamily: SERIF, fontWeight: 500, fontSize: 124, letterSpacing: '-0.02em', lineHeight: 1}}>FREE</span>
        </div>
      </div>
      <div style={{position: 'absolute', top: 1520, left: 0, right: 0, textAlign: 'center', opacity: interpolate(t, [60, 70], [0, 1], CL)}}>
        <div style={{fontFamily: SERIF, fontSize: 34, color: C.ink}}>3 thank-yous free · Plus ₦2,000 · Premium ₦5,000</div>
        <div style={{...hand, fontSize: 52, marginTop: 10}}>pay once, not every month</div>
        <Small style={{marginTop: 26, fontSize: 24}}>Link in bio</Small>
      </div>
    </AbsoluteFill>
  );
};

// ---------- finishing ----------
const Finish = ({f}) => (
  <>
    <svg width={W} height={H} style={{position: 'absolute', inset: 0, opacity: 0.08, mixBlendMode: 'multiply', pointerEvents: 'none'}}>
      <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed={f} stitchTiles="stitch" /><feColorMatrix type="saturate" values="0" /></filter>
      <rect width="100%" height="100%" filter="url(#grain)" />
    </svg>
    <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 60%, rgba(0,0,0,0.08) 100%)'}} />
    <div style={{position: 'absolute', left: 64, top: 70, ...italic, fontSize: 40, color: '#fff', mixBlendMode: 'difference'}}>Ẹ ṣé</div>
  </>
);

const Reel = () => {
  const f = useCurrentFrame();
  const [handle] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(['400 100px Fraunces', 'italic 400 100px Fraunces', '500 100px Fraunces', '500 100px Caveat', '700 100px Caveat']
      .map((s) => document.fonts.load(s, 'Ẹ ṣé aA'))).then(() => document.fonts.ready).then(() => continueRender(handle));
  }, [handle]);
  let scene;
  if (f < T.steps) scene = <Pendulum f={f} />;
  else if (f < T.torch) scene = <Steps f={f} />;
  else if (f < T.end) scene = <Torch f={f} />;
  else scene = <EndCard f={f} />;
  return (
    <AbsoluteFill style={{background: C.paper}}>
      {scene}
      <Finish f={f} />
      <Audio src={staticFile('score.wav')} />
    </AbsoluteFill>
  );
};

registerRoot(() => <Composition id="Reel" component={Reel} durationInFrames={DURATION} fps={FPS} width={W} height={H} />);
