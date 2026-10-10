import {useCurrentFrame} from 'remotion';
import manifest from './edit-manifest.json';

/** Speech anchors are generated from VOICEVOX mora durations in prepare_voice.py. */
export function useDiagramTiming() {
  const frame = useCurrentFrame();
  const cues = manifest.visualCues as Record<string, {frame: number}>;
  const at = (id: string) => cues[id]?.frame ?? Infinity;
  const show = (id: string) => Math.max(0, Math.min(1, (frame - at(id)) / 6));
  const between = (start: string, end: string) =>
    Math.max(0, Math.min(1, (frame - at(start)) / Math.max(1, at(end) - at(start))));
  return {frame, at, show, between};
}
