import {Relaxed} from './Relaxed';
import {Familiar} from './Familiar';
import relaxed from './relaxed-manifest.json';
import './style.css';
import {SoundVariants} from './SoundVariants';
import {SoloSfx} from './SoloSfx';
import {SobayaDuo} from './SobayaDuo';
import sobaya from './sobaya-manifest.json';
import {Solo} from './Solo';
import solo from './solo-manifest.json';
import {Duo} from './Duo';
import duo from './duo-manifest.json';
import {Composition} from 'remotion';
import manifestJson from './edit-manifest.json';
import {EditComposition} from './Composition';
import type {EditManifest} from './types';

const manifest = manifestJson as EditManifest;

export const RemotionRoot: React.FC = () => {
  return (
    <>
    <Composition id="YumemiFamiliar" component={Familiar} width={1920} height={1080} fps={30} durationInFrames={relaxed.durationInFrames}/>
    <Composition id="YumemiRelaxed" component={Relaxed} width={1920} height={1080} fps={30} durationInFrames={relaxed.durationInFrames}/>
    {(["keynote","comedy","intense"] as const).map(variant=><Composition key={variant} id={`YumemiSound-${variant}`} component={SoundVariants} defaultProps={{variant}} width={1920} height={1080} fps={30} durationInFrames={solo.durationInFrames}/>)}
    <Composition id="YumemiSoloSfx" component={SoloSfx} width={1920} height={1080} fps={30} durationInFrames={solo.durationInFrames} />
    <Composition id="YumemiSobaya" component={SobayaDuo} width={1920} height={1080} fps={30} durationInFrames={sobaya.durationInFrames} />
    <Composition id="YumemiSolo" component={Solo} width={1920} height={1080} fps={30} durationInFrames={solo.durationInFrames} />
    <Composition id="YumemiDuo" component={Duo} width={1920} height={1080} fps={30} durationInFrames={duo.durationInFrames} />
    <Composition
      id={manifest.composition.id}
      component={EditComposition}
      width={manifest.composition.width}
      height={manifest.composition.height}
      fps={manifest.composition.fps}
      durationInFrames={manifest.composition.durationInFrames}
      defaultProps={{manifest}}
    />
    </>
  );
};
