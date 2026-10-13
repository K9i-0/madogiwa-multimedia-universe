import type {CSSProperties} from 'react';
import {memberColors} from '../../../00_TEMPLATES/subtitles/member-colors';

// White information-program palette. Focus never makes other text translucent.
export const theme = {
  paper: '#FFFFFF', ink: '#172B46', blue: '#174E9F', muted: '#46566C',
  border: '#718096', yellow: '#FFD447', alert: '#AD2443',
} as const;

export const headingStyle: CSSProperties = {
  fontSize: 32, fontWeight: 700, marginBottom: 28, lineHeight: 1.5,
  color: theme.blue, borderBottom: `6px solid ${theme.yellow}`, paddingBottom: 8,
};

export const cardStyle = (active = true, show = true): CSSProperties => ({
  flex: 1, minWidth: 0, boxSizing: 'border-box', padding: '20px 10px',
  borderRadius: 8, border: `3px solid ${active ? theme.blue : theme.border}`,
  background: active ? theme.yellow : theme.paper, color: theme.ink,
  visibility: show ? 'visible' : 'hidden', fontSize: 27, fontWeight: 600,
  lineHeight: 1.65, whiteSpace: 'pre-line',
});

// Preserve the canonical purple/pink hues; darken locally for white backgrounds.
const darker = (hex: string) => '#' + hex.slice(1).match(/../g)!
  .map(x => Math.round(parseInt(x, 16) * .68).toString(16).padStart(2, '0')).join('');
export const captionColors = {
  yametaro: darker(memberColors.yametaro), takosan: darker(memberColors.takosan),
};
