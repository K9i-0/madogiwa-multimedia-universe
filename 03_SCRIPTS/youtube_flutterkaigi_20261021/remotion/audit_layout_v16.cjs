const {bundle}=require('@remotion/bundler');
const {selectComposition,renderStill,openBrowser}=require('@remotion/renderer');
const fs=require('fs'),path=require('path');
(async()=>{
 const m=JSON.parse(fs.readFileSync('src/edit-manifest.json'));const out=process.env.AUDIT_OUT||'out/layout_v16';fs.mkdirSync(out,{recursive:true});
 const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});const browser=await openBrowser('chrome');
 const orig=browser.newPage.bind(browser);let current;const reports=[];
 browser.newPage=async opts=>{const page=await orig(opts);const close=page.close.bind(page);page.close=async(...args)=>{try{const result=await page.evaluate(()=>{
 const box=e=>{const b=e.getBoundingClientRect();return {x:b.x,y:b.y,w:b.width,h:b.height,right:b.right,bottom:b.bottom};};
 const visible=e=>{for(let p=e;p;p=p.parentElement){if(Number(getComputedStyle(p).opacity)<.25)return false;}return true;};
 const cards=[...document.querySelectorAll('[data-card]')].map(g=>{const r=[...g.children].filter(e=>e.tagName==='rect').find(e=>e.getAttribute('stroke'));if(!r)return null;const b=box(r);return {rect:b,text:[...g.querySelectorAll('text')].map(t=>({text:t.textContent,box:box(t),size:getComputedStyle(t).fontSize})).filter(t=>t.box.x<b.x+10||t.box.right>b.right-10||t.box.y<b.y+6||t.box.bottom>b.bottom-6)};}).filter(r=>r&&r.text.length);
 const ts=[...document.querySelectorAll('[data-center] svg text')].filter(visible).map(t=>({text:t.textContent,box:box(t)}));const overlap=[];
 for(let i=0;i<ts.length;i++)for(let j=i+1;j<ts.length;j++){const a=ts[i].box,b=ts[j].box;const w=Math.min(a.right,b.right)-Math.max(a.x,b.x),h=Math.min(a.bottom,b.bottom)-Math.max(a.y,b.y);if(w>4&&h>5)overlap.push([ts[i].text,ts[j].text]);}
 const outside=ts.filter(t=>t.box.x<120||t.box.right>1160||t.box.y<15||t.box.bottom>558);
 return {cards,overlap,outside};});reports.push({...current,...result});}catch(e){console.log('audit eval',String(e));}return close(...args);};return page;};
 const comp=await selectComposition({serveUrl,id:'FlutterKaigi',puppeteerInstance:browser});
 for(const [i,d] of m.dialogue.entries()){
  if(process.env.AUDIT_VIEWS&&!process.env.AUDIT_VIEWS.split(",").includes(d.view))continue;
  current={id:d.id,view:d.view,frame:d.startFrame+Math.floor(d.durationInFrames*.75)};
  await renderStill({serveUrl,composition:comp,frame:current.frame,output:`${out}/${String(i).padStart(3,'0')}_${d.view}.png`,puppeteerInstance:browser});
  if(i%20===0)console.log(i,d.view);
 }
 fs.writeFileSync(`${out}/report.json`,JSON.stringify(reports,null,2));await browser.close({silent:true});console.log('done',reports.length);
})().catch(e=>{console.error(e);process.exit(1)});
