export type Who = 'yametaro' | 'takosan';
export type Mood = 'normal'|'happy'|'surprise'|'worry'|'bored'|'angry'|'sad'|'smug';
export type Dialogue = {
  id: string; who: Who; text: string; caption?: string; captionFontSize?: number;
  captionSegments?: {startFrame:number;endFrame:number;text:string}[];
  moods?: Partial<Record<Who,Mood>>; view: string; chapter: number|string;
  focus?: string|number; startFrame: number; durationInFrames: number; envelope: number[];
};
export type Manifest = {
  dialogue: Dialogue[];
  audioSrc?: string;
  scenes?: {view:string;startFrame:number;durationInFrames:number}[];
  composition: {width:number;height:number;fps:number;durationInFrames:number};
};
