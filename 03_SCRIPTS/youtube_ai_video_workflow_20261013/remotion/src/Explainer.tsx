import React from 'react';
import {AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, staticFile, useCurrentFrame, interpolate} from 'remotion';
import rawManifest from './edit-manifest.json';
import {DuoSprite, Mood} from './DuoSprite';
import expressions from './expressions-v10.json';
import {theme, captionColors} from './theme';

type Dialogue = {id?: string; who: string; text: string; caption: string; captionFontSize?: number; captionSegments?: {startFrame:number;endFrame:number;text:string}[]; mood?: string; view: string; chapter?: string; startFrame: number; durationInFrames: number; envelope: number[]};
type Clip = {src: string; startFrame: number; durationInFrames: number; sourceStartFrame: number; label: string; layout?: 'full' | 'comparison'; tag?: string};
type Manifest = {dialogue: Dialogue[]; clips: Clip[]; creditsStartFrame: number; composition: {durationInFrames: number}};
const {ink, muted, paper} = theme;
const Pic: React.FC<{name: string; w?: number; h?: number}> = ({name,w=710,h=390}) => <Img src={staticFile(name)} style={{width:w,height:h,objectFit:'contain'}}/>;
import {VisualAid} from './VisualAid';

const ClipPlayer: React.FC<{clip: Clip}> = ({clip}) => {
  const comparison = clip.layout === 'comparison';
  return <AbsoluteFill style={{background: paper}}>
    <div style={{position: 'absolute', top: comparison ? 22 : 16, left: 70, right: 70, height: comparison ? 74 : 42, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 5}}>
      {clip.tag && <div style={{fontSize: 18, color: muted}}>{clip.tag}</div>}
      <div style={{fontSize: comparison ? 27 : 24, fontWeight: 700, color: theme.blue}}>{clip.label}</div>
    </div>
    <Sequence from={clip.startFrame} durationInFrames={clip.durationInFrames}>
      <OffthreadVideo muted src={staticFile(clip.src)} startFrom={clip.sourceStartFrame} style={{position: 'absolute', left: comparison ? 136 : 72, top: comparison ? 113 : 69, width: comparison ? 1008 : 1136, height: comparison ? 567 : 639, objectFit: 'contain', background: '#15272a'}}/>
    </Sequence>
  </AbsoluteFill>;
};

export const Explainer: React.FC<{manifest?: Manifest; audioSrc?: string}> = ({manifest, audioSrc='mixed.wav'}) => {
  const m=manifest ?? rawManifest as Manifest;
  const f = useCurrentFrame();
  const active = m.dialogue.find(d => f >= d.startFrame && f < d.startFrame + d.durationInFrames);
  const previousIndex = m.dialogue.reduce((last, d, i) => f >= d.startFrame ? i : last, -1);
  const previous = m.dialogue[previousIndex];
  const caption = active?.captionSegments?.find(s=>f-active.startFrame>=s.startFrame&&f-active.startFrame<s.endFrame)?.text ?? active?.caption;
  const clip = m.clips.find(c => f >= c.startFrame && f < c.startFrame + c.durationInFrames);
  const view = previous?.view ?? 'opening';
  // Narration IDs are not scene boundaries. Keep reference images visible across
  // speaker/caption changes; VisualAid owns intentional changes and highlights.
  return <AbsoluteFill style={{background: paper, fontFamily: '"Hiragino Sans", sans-serif', color: ink}}>
    <Audio src={staticFile(audioSrc)}/>
    {clip ? <ClipPlayer clip={clip}/> : <>
      <div style={{position: 'absolute', left: 260, top: 24, width: 760, height: 531, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center'}}><VisualAid view={view} frame={f} utterance={previous}/></div>
      {(['yametaro','takosan'] as const).map(who => {
        const speaking=active?.who===who; const local=active?f-active.startFrame:0;
        const peak=Math.max(...(active?.envelope??[0]));
        const open=speaking&&(active?.envelope[Math.floor(local/2)*2]??0)>Math.max(.0025,peak*.15);
        const mood=((expressions as Record<string,Record<string,Mood>>)[previous?.id??'v000']??{})[who]??'normal';
        return <DuoSprite key={who} who={who} speaking={speaking} open={open} mood={mood} local={local}/>;
      })}
      {active && <div style={{position: 'absolute', left: 245, right: 245, bottom: 29, minHeight: 110, display: 'flex', alignItems: 'center', justifyContent: 'center'}}><div style={{fontSize: active.captionFontSize ?? 29, fontWeight: 700, lineHeight: 1.65, textAlign: 'center', whiteSpace: 'pre-line', color: active.who === 'yametaro' ? captionColors.yametaro : captionColors.takosan, WebkitTextStroke: '3px #fff', paintOrder: 'stroke fill', textShadow: 'none'}}>{caption}</div></div>}
    </>}
    <AbsoluteFill style={{background: paper, opacity: interpolate(f, [m.composition.durationInFrames - 30, m.composition.durationInFrames - 1], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}/>
  </AbsoluteFill>;
};
