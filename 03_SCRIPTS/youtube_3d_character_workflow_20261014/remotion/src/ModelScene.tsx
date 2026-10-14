import React,{Suspense,useMemo,useLayoutEffect} from 'react';
import {ThreeCanvas} from '@remotion/three';
import {useLoader,useThree} from '@react-three/fiber';
import {staticFile,delayRender,continueRender} from 'remotion';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {clone} from 'three/examples/jsm/utils/SkeletonUtils.js';
import * as T from 'three';
export type ModelKind='sobaya'|'takosan'|'fukuchan';
function Actor({kind,t,mode,bones,handle,close}:{kind:ModelKind;t:number;mode:string;bones:boolean;handle:number;close:boolean}){
 const {gl,scene:world,camera}=useThree();
 const gltf=useLoader(GLTFLoader,staticFile(`models/${kind}.glb`));
 const {scene,mixer,rest,skeleton}=useMemo(()=>{const scene=clone(gltf.scene);const rest:{o:T.Object3D;p:T.Vector3;q:T.Quaternion;s:T.Vector3}[]=[];scene.traverse(o=>{rest.push({o,p:o.position.clone(),q:o.quaternion.clone(),s:o.scale.clone()});if(o instanceof T.Mesh){o.frustumCulled=false;}});const skeleton=new T.SkeletonHelper(scene);skeleton.material=new T.LineBasicMaterial({color:'#e4482e',depthTest:false,transparent:true,opacity:.9});skeleton.renderOrder=999;return{scene,mixer:new T.AnimationMixer(scene),rest,skeleton};},[gltf]);
 useLayoutEffect(()=>{
  mixer.stopAllAction();mixer.time=0;rest.forEach(({o,p,q,s})=>{o.position.copy(p);o.quaternion.copy(q);o.scale.copy(s);});
  const clipName=kind==='takosan'?(mode==='wave'?'Wave':'Idle'):kind==='fukuchan'?'Idle':mode==='walk'?'Walk':mode==='greeting'?'Greeting':'CharacterSheet_MugStand';
  const clip=gltf.animations.find(a=>a.name===clipName);if(!clip)throw new Error(`Missing clip ${kind}:${clipName}`);
  const action=mixer.clipAction(clip);action.reset().play();mixer.setTime(t%clip.duration);
  if(kind==='takosan'&&mode!=='wave'){
   // Closed-form fixed-speed evaluation of the adopted curl/E motion in tools/takosan_float_motion.mjs.
   const phase=t*(1.8+1.2*.85);let count=0;
   for(const {o,q} of rest){const m=/^Tentacle([1-6])[._]?(Base|Mid|Tip)$/.exec(o.name);if(!m)continue;count++;
    const i=+m[1]-1,j=['Base','Mid','Tip'].indexOf(m[2]),d=j*.8;
    o.quaternion.copy(q).multiply(new T.Quaternion().setFromEuler(new T.Euler((.035+j*.19)*Math.sin(phase*.8-i*.7-d)+.4*.025*j,(.02+j*.02)*Math.sin(phase*.8-i*.7),(.025+j*.11)*Math.cos(phase*.8-i*.7-d))));
   }if(count!==18)throw new Error(`Tentacle joints ${count}`);
  }
  scene.updateMatrixWorld(true);skeleton.updateMatrixWorld(true);camera.position.set(0,close?1.58:1.35,close?1.7:3.8);camera.lookAt(0,close?1.48:.95,0);camera.updateMatrixWorld(true);camera.updateProjectionMatrix();world.updateMatrixWorld(true);gl.render(world,camera);continueRender(handle);
 },[scene,mixer,rest,gltf,t,kind,mode,skeleton]);
 const yaw=mode==='turn'?t*.36:mode==='walk'?.55:mode==='face'?Math.sin(t*.5)*.55:.12;
 return <><group rotation={[0,yaw,0]} position={[0,kind==='takosan'&&mode!=='wave'?.15+.025*Math.sin(t*1.7):0,0]}><primitive object={scene}/></group>{bones&&<primitive object={skeleton}/>}</>;
}
export const ModelScene:React.FC<{kind?:ModelKind;t:number;mode?:string;bones?:boolean;close?:boolean;width?:number;height?:number}>=({kind='sobaya',t,mode='turn',bones=false,close=false,width=760,height=340})=>{const handle=useMemo(()=>delayRender('Loading '+kind,{timeoutInMilliseconds:120000}),[kind]);return <ThreeCanvas width={width} height={height} camera={{fov:34,near:.05,far:40}} gl={{antialias:true,alpha:false,preserveDrawingBuffer:true}}><color attach="background" args={['#edf2ef']}/><hemisphereLight args={['#ffffff','#8a9d92',2.4]}/><directionalLight position={[3,5,4]} intensity={2.8}/><directionalLight position={[-3,2,-2]} intensity={1.3}/><gridHelper args={[12,24,'#afc4b8','#dce5df']}/><Suspense fallback={null}><Actor kind={kind} t={t} mode={mode} bones={bones} handle={handle} close={close}/></Suspense></ThreeCanvas>};
