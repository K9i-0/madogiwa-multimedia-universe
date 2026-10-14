import React from 'react';
import {Img, staticFile, useCurrentFrame} from 'remotion';
import actingPlan from '../acting-plan-v3.json';
import type {Mood} from './DuoSprite';

export type DuoWho = 'yametaro' | 'takosan';
type Motion = 'nod' | 'tilt' | 'hop' | 'recoil';
type Beat = {atFrame: number; mood?: Mood; motion?: Motion; durationInFrames?: number};
type Performance = {mood: Mood; beats: Beat[]};
type ActingRow = {yametaro: Performance; takosan: Performance};

export interface DuoSpriteV3Props {
  who: DuoWho;
  /** Stable dialogue ID, including when this character is listening. */
  id: string;
  speaking: boolean;
  /** Audio envelope mouth state; ignored for Takosan, and when not speaking. */
  open: boolean;
  /** Integer frames since the current dialogue began (not scene-local time). */
  local: number;
  durationInFrames?: number;
}

const rows = actingPlan.dialogue as unknown as Record<string, ActingRow>;
const neutral: Performance = {mood: 'normal', beats: []};

/** Exported for frame/asset audits. No state, random choices or keyword matching. */
export function getActingStateV3(id: string, who: DuoWho, local: number) {
  const performance = rows[id]?.[who] ?? neutral;
  let mood = performance.mood;
  let motion: Beat | undefined;
  for (const beat of performance.beats) {
    if (local >= beat.atFrame) {
      if (beat.mood) mood = beat.mood;
      if (beat.motion && local < beat.atFrame + (beat.durationInFrames ?? 30)) motion = beat;
    }
  }
  return {mood, motion};
}

// These poses share their opaque foot baselines to within two source pixels.
// Ignore the near-transparent antialiasing/noise at the PNG canvas edges.
const footY: Record<DuoWho, Record<Mood, number>> = {
  yametaro: {normal: 1481, happy: 1483, surprise: 1482, worry: 1483, bored: 1482, angry: 1483, sad: 1483, smug: 1482},
  takosan: {normal: 1276, happy: 1278, surprise: 1278, worry: 1278, bored: 1277, angry: 1278, sad: 1278, smug: 1276},
};

// Existing expression sheets have tiny mouth marks. Use only the already
// mouthless normal texture in these small, feathered face regions. Eyes, hood,
// hands and pose remain the actual expression asset; no generated face patch.
// Coordinates refer to the original 1164 × 1351 canvas.
const mouthRegion: Partial<Record<Mood, [number, number, number, number]>> = {
  happy: [470, 577, 46, 27],
  worry: [468, 586, 37, 24],
  bored: [469, 572, 32, 16],
  angry: [467, 581, 48, 27],
  sad: [475, 591, 38, 25],
  smug: [467, 568, 43, 25],
};

/** The same artwork compositor is also used in the eight-expression audit. */
export function DuoSpriteArtworkV3({who, mood, open = false, blink = false}: {who: DuoWho; mood: Mood; open?: boolean; blink?: boolean}) {
  const tako = who === 'takosan';
  const imageStyle: React.CSSProperties = {position: 'absolute', inset: 0, width: '100%', height: '100%'};
  const region = tako ? mouthRegion[mood] : undefined;
  const mouthMask = region ? `radial-gradient(ellipse ${region[2] / 1164 * 100}% ${region[3] / 1351 * 100}% at ${region[0] / 1164 * 100}% ${region[1] / 1351 * 100}%,black 68%,transparent 100%)` : undefined;
  const eyeMask = 'radial-gradient(ellipse 5.4% 5% at 32.8% 37.6%,black 80%,transparent 100%),radial-gradient(ellipse 5.8% 5% at 49% 37.7%,black 80%,transparent 100%)';
  const mouth = !tako && open ? 'open' : 'closed';
  return <>
    <Img src={staticFile(`expressions/${who}_${mood}_${mouth}.png`)} style={imageStyle}/>
    {mouthMask && <Img src={staticFile('expressions/takosan_normal_closed.png')} style={{...imageStyle, maskImage: mouthMask, WebkitMaskImage: mouthMask}}/>}
    {tako && mood === 'normal' && blink && <Img src={staticFile('takosan_blink.png')} style={{...imageStyle, maskImage: eyeMask, WebkitMaskImage: eyeMask}}/>}
  </>;
}

export function DuoSpriteV3({who, id, speaking, open, local, durationInFrames}: DuoSpriteV3Props) {
  const frame = useCurrentFrame();
  const tako = who === 'takosan';
  const {mood, motion} = getActingStateV3(id, who, Math.max(0, local));
  const width = tako ? 158 : 146;
  const canvasWidth = tako ? 1164 : 1024;
  const height = width * (tako ? 1351 / 1164 : 1536 / 1024);
  const direction = tako ? -1 : 1;
  let dy = 0;
  let dx = 0;
  let rotation = 0;
  if (motion && (durationInFrames === undefined || local < durationInFrames)) {
    const progress = Math.min(1, Math.max(0, (local - motion.atFrame) / (motion.durationInFrames ?? 30)));
    const pulse = Math.sin(Math.PI * progress) ** 2;
    if (motion.motion === 'nod') {
      dy = pulse * 2.2;
      rotation = direction * Math.sin(2 * Math.PI * progress) * pulse * .8;
    } else if (motion.motion === 'tilt') {
      rotation = direction * pulse * 2;
    } else if (motion.motion === 'hop') {
      dy = -pulse * 5;
    } else if (motion.motion === 'recoil') {
      dx = -direction * pulse * 2;
      rotation = -direction * pulse * 1.4;
    }
  }
  const footOffset = (footY[who].normal - footY[who][mood]) * width / canvasWidth;
  const blink = tako && mood === 'normal' && (frame + 23) % 149 < 4;
  return <div data-acting-id={id} data-acting-who={who} data-acting-mood={mood} style={{position: 'absolute', left: tako ? 1122 : 16, bottom: 35, width, height, transformOrigin: '50% 96%', transform: `translate(${dx}px,${dy}px) rotate(${rotation}deg)`, pointerEvents: 'none'}}>
    <div style={{position: 'absolute', inset: 0, transform: `translateY(${footOffset}px)${tako ? '' : ' scaleX(-1)'}`}}>
      <DuoSpriteArtworkV3 who={who} mood={mood} open={speaking && open} blink={blink}/>
    </div>
  </div>;
}
