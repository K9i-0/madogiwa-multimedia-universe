import React from 'react';

const GREEN = '#176B47';
const tabs = ['完成例', '回転動画', 'Tripoで生成', '料金と選び方', '手直し', '骨と動作', '活用', 'まとめ'];

/** Keep the spreadsheet colour and tabs; remove decorative application controls. */
export function SpreadsheetFrameV3({chapter, progress, children}: {
  chapter: string; progress: number; children: React.ReactNode;
}) {
  const section = Math.max(0, Number(chapter.split('.')[0]) - 1);
  return <>
    <div style={{position: 'absolute', inset: 0, background: '#fff'}} />
    <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 35, background: GREEN,
      color: '#fff', display: 'flex', alignItems: 'center', padding: '0 24px', fontSize: 17, fontWeight: 650}}>
      窓際族物語<span style={{opacity: .4, margin: '0 14px'}}>/</span>画像から、動く3Dへ
    </div>
    {children}
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 31,
      background: '#f0f3f1', borderTop: '1px solid #bccbc1', display: 'flex', paddingLeft: 30}}>
      {tabs.map((tab, i) => <div key={tab} style={{position: 'relative', fontSize: 14, padding: '5px 18px',
        background: section === i ? '#fff' : 'transparent', color: section === i ? GREEN : '#647168',
        fontWeight: section === i ? 700 : 400, borderRight: '1px solid #d6dfd9'}}>
        {tab}{section === i && <div style={{position: 'absolute', bottom: 0, left: 0, height: 3,
          width: `${Math.max(4, progress * 100)}%`, background: GREEN}} />}
      </div>)}
    </div>
  </>;
}
