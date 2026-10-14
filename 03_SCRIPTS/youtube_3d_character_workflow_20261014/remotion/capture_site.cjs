const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--enable-webgl','--use-gl=angle','--use-angle=metal']});
const c=await b.newContext({viewport:{width:1280,height:900},deviceScaleFactor:1,recordVideo:{dir:'out/site_record',size:{width:1280,height:900}}});const p=await c.newPage();
await p.goto('https://madogiwa.work/characters/sobaya',{waitUntil:'networkidle',timeout:60000});console.log((await p.locator('body').innerText()).slice(0,2200));
await p.screenshot({path:'public/site_character.png'});
await p.getByRole('button',{name:/3Dで見る/}).click();await p.getByRole('button',{name:'顔アップ',exact:true}).waitFor();await p.getByRole('button',{name:'顔アップ',exact:true}).waitFor();await p.waitForFunction(()=>!document.querySelector('.j-model-framing button')?.disabled,{},{timeout:60000});
await p.screenshot({path:'public/site_3d.png'});
let box=await p.locator('canvas[aria-label*="ドラッグ"]').boundingBox();if(box){await p.mouse.move(box.x+box.width*.55,box.y+box.height*.5);await p.mouse.down();await p.mouse.move(box.x+box.width*.8,box.y+box.height*.5,{steps:45});await p.mouse.up();}
await p.waitForTimeout(2000);await p.getByRole('button',{name:'顔アップ',exact:true}).click();await p.waitForTimeout(2200);await p.getByRole('button',{name:'全身',exact:true}).click();await p.waitForTimeout(1000);
await p.getByRole('button',{name:'たこさん',exact:true}).click();await p.waitForTimeout(3500);let wave=p.getByRole('button',{name:'手を振る',exact:true});if(await wave.count())await wave.click();await p.waitForTimeout(3500);await p.screenshot({path:'public/site_tako.png'});
await p.getByRole('button',{name:'福ギュン',exact:true}).click();await p.waitForFunction(()=>!document.querySelector('.j-model-framing button')?.disabled,{},{timeout:60000});await p.waitForTimeout(1500);await p.screenshot({path:'public/site_fuku.png'});
const video=p.video();await c.close();await video.saveAs('public/site.webm');
const c2=await b.newContext({viewport:{width:1280,height:900}});const p2=await c2.newPage();await p2.goto('https://madogiwa.work/camera/sobaya',{waitUntil:'networkidle'});await p2.screenshot({path:'public/ar.png'});console.log('AR', (await p2.locator('body').innerText()).slice(0,1500));await b.close();})();
