import React from 'react';
import {ModelSceneV2} from './ModelSceneV2';
import {VisualV5} from './VisualV5';

type Props = React.ComponentProps<typeof VisualV5>;

/** Keep the invitation brief; the narration explains what was learned by trial and error. */
function Comments({t}: {t: number}) {
  return <div style={{width: 1000, height: 470, display: 'flex', flexDirection: 'column',
    color: '#15372a', background: '#fff', overflow: 'hidden'}}>
    <div style={{height: 49, flexShrink: 0, borderBottom: '2px solid #176b47',
      fontSize: 31, fontWeight: 800, lineHeight: 1.25}}>Tripo・リグの作り方</div>
    <div style={{flex: 1, minHeight: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 38}}>
      <div style={{width: 500, height: 397, overflow: 'hidden', flexShrink: 0}}>
        <ModelSceneV2 kind="sobaya" t={t} mode="greeting" bones width={500} height={397} zoom={.90} />
      </div>
      <div style={{width: 432, paddingLeft: 8, boxSizing: 'border-box'}}>
        <div style={{fontSize: 31, fontWeight: 700}}>おすすめの方法、</div>
        <div style={{marginTop: 18, fontSize: 38, fontWeight: 800, lineHeight: 1.55, color: '#176b47'}}>
          コメントで<br />教えてください
        </div>
      </div>
    </div>
  </div>;
}

export function VisualV6(props: Props) {
  if (props.view === 'comments') return <Comments t={props.t} />;
  return <VisualV5 {...props} />;
}
