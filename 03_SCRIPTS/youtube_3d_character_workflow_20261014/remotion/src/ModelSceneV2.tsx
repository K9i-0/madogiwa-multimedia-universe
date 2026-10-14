import React,{Suspense,useMemo,useLayoutEffect} from 'react';
import {ThreeCanvas} from '@remotion/three';
import {useLoader,useThree} from '@react-three/fiber';
import {staticFile,delayRender,continueRender} from 'remotion';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {clone} from 'three/examples/jsm/utils/SkeletonUtils.js';
import * as T from 'three';
export type ModelKind='sobaya'|'takosan'|'fukuchan';
type Props={kind?:ModelKind;t:number;mode?:string;bones?:boolean;close?:boolean;width?:number;height?:number;zoom?:number;freeze?:boolean};
function Actor({kind,t,mode,bones,handle,close,zoom,freeze}:{kind:ModelKind;t:number;mode:string;bones:boolean;handle:number;close:boolean;zoom:number;freeze:boolean}){
 const {gl,scene:world,camera}=useThree();const gltf=useLoader(GLTFLoader,staticFile(`models/${kind}.glb`));
 const {scene,mixer,rest,skeleton,dots}=useMemo(()=>{
  const scene=clone(gltf.scene);const rest:{o:T.Object3D;p:T.Vector3;q:T.Quaternion;s:T.Vector3}[]=[];const dots=new T.Group();
  scene.traverse(o=>{rest.push({o,p:o.position.clone(),q:o.quaternion.clone(),s:o.scale.clone()});if(o instanceof T.Mesh){o.frustumCulled=false;o.castShadow=true;o.receiveShadow=true;}if(o instanceof T.Bone&&/arm|forearm|hand|leg|hip|spine|head|tentacle/i.test(o.name)){const dot=new T.Mesh(new T.SphereGeometry(kind==='takosan'?.009:.014,8,6),new T.MeshBasicMaterial({color:'#e45735',depthTest:false}));dot.userData.bone=o;dot.renderOrder=1000;dots.add(dot);}});
  const skeleton=new T.SkeletonHelper(scene);skeleton.material=new T.LineBasicMaterial({color:'#db3c20',depthTest:false,transparent:true,opacity:1});skeleton.renderOrder=999;
  return {scene,mixer:new T.AnimationMixer(scene),rest,skeleton,dots};
 },[gltf,kind]);
 const yaw=mode==='turn'?-.3+t*.27:mode==='walk'?.30:mode==='face'?Math.sin(t*.35)*.45:0;
 useLayoutEffect(()=>{
  mixer.stopAllAction();mixer.time=0;rest.forEach(({o,p,q,s})=>{o.position.copy(p);o.quaternion.copy(q);o.scale.copy(s);});
  const name=kind==='takosan'?(mode==='wave'?'Wave':'Idle'):kind==='fukuchan'?'Idle':mode==='walk'?'Walk':mode==='greeting'?'Greeting':mode==='arm'?'Test_ArmRaise':'Hybrid_Idle_A';
  const clip=gltf.animations.find(a=>a.name===name);if(!clip)throw new Error(`Missing clip ${kind}:${name}`);mixer.clipAction(clip).reset().play();mixer.setTime(freeze?0:t%clip.duration);
  if(kind==='takosan'&&mode!=='wave'){
   const phase=t*2.82;let count=0;for(const {o,q} of rest){const m=/^Tentacle([1-6])[._]?(Base|Mid|Tip)$/.exec(o.name);if(!m)continue;count++;const i=+m[1]-1,j=['Base','Mid','Tip'].indexOf(m[2]),d=j*.8;
    o.quaternion.copy(q).multiply(new T.Quaternion().setFromEuler(new T.Euler((.035+j*.19)*Math.sin(phase*.8-i*.7-d)+.01*j,(.02+j*.02)*Math.sin(phase*.8-i*.7),(.025+j*.11)*Math.cos(phase*.8-i*.7-d))));
   }if(count!==18)throw new Error(`Tentacle joints ${count}`);
  }
  world.updateMatrixWorld(true);scene.updateMatrixWorld(true);skeleton.updateMatrixWorld(true);for(const dot of dots.children){(dot.userData.bone as T.Bone).getWorldPosition(dot.position);}dots.updateMatrixWorld(true);
  const z=close?1.58:kind==='takosan'?3.2:3.85;camera.position.set(0,close?1.60:1.23,z/zoom);camera.lookAt(0,close?1.49:.94,0);camera.updateMatrixWorld(true);camera.updateProjectionMatrix();gl.render(world,camera);continueRender(handle);
 },[scene,mixer,rest,gltf,t,kind,mode,skeleton,dots,close,zoom,freeze,bones,yaw]);
 return <><group rotation={[0,yaw,0]} position={[0,kind==='takosan'&&mode!=='wave'?.15+.025*Math.sin(t*1.7):0,0]}><primitive object={scene}/></group>{bones&&<><primitive object={skeleton}/><primitive object={dots}/></>}</>;
}
export const ModelSceneV2:React.FC<Props>=({kind='sobaya',t,mode='turn',bones=false,close=false,width=1000,height=390,zoom=1,freeze=false})=>{
 const handle=useMemo(()=>delayRender('Loading v2 '+kind,{timeoutInMilliseconds:120000}),[kind]);
 return <ThreeCanvas width={width} height={height} shadows camera={{fov:32,near:.05,far:40}} gl={{antialias:true,alpha:false,preserveDrawingBuffer:true,toneMapping:T.ACESFilmicToneMapping,toneMappingExposure:1.15}}>
 <color attach="background" args={['#eef3ef']}/><hemisphereLight args={['#ffffff','#a3b1a6',2.0]}/><directionalLight position={[3,5,4]} intensity={3.2} castShadow shadow-mapSize={[1024,1024]} shadow-camera-left={-3} shadow-camera-right={3} shadow-camera-top={4} shadow-camera-bottom={-2} shadow-normalBias={.025}/><directionalLight position={[-3,2,-2]} intensity={1.4}/>
 <mesh rotation={[-Math.PI/2,0,0]} position={[0,-.018,0]} receiveShadow><planeGeometry args={[200,200]}/><meshStandardMaterial color="#eef3ef" roughness={1}/></mesh>
 <Suspense fallback={null}><Actor kind={kind} t={t} mode={mode} bones={bones} handle={handle} close={close} zoom={zoom} freeze={freeze}/></Suspense></ThreeCanvas>;
};
