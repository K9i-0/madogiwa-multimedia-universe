import {Composition} from 'remotion';
import data from './edit-manifest.json';
import ending from './ending-edit.json';
import {EditComposition} from './Composition';
import {ExteriorEnding} from './ExteriorEnding';
import h3 from './h3-edit.json';
import {H3Edit} from './H3Edit';
export const RemotionRoot: React.FC = () => <>
 <Composition id={data.composition.id} component={EditComposition}
 width={data.composition.width} height={data.composition.height}
 fps={data.composition.fps} durationInFrames={data.composition.durationInFrames} />
 <Composition id={ending.composition.id} component={ExteriorEnding}
 width={ending.composition.width} height={ending.composition.height}
 fps={ending.composition.fps} durationInFrames={ending.composition.durationInFrames} />
<Composition id={h3.composition.id} component={H3Edit} width={h3.composition.width} height={h3.composition.height} fps={h3.composition.fps} durationInFrames={h3.composition.durationInFrames} />
</>;
