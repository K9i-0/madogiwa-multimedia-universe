const fs=require('fs'),path=require('path');
const {bundle}=require('@remotion/bundler');
const {renderStill,selectComposition,openBrowser}=require('@remotion/renderer');
(async()=>{const dir=path.resolve('../thumbnail');const data=n=>'data:image/png;base64,'+fs.readFileSync(path.join(dir,n)).toString('base64');const inputProps={game:data('game_capture.png'),zunda:data('zundamon_overlay.png')};const serveUrl=await bundle({entryPoint:path.resolve('src/Thumbnail.tsx')});const browser=await openBrowser('chrome');const composition=await selectComposition({serveUrl,id:'Thumbnail',inputProps,puppeteerInstance:browser});
for(const overlay of [false,true])await renderStill({serveUrl,composition:{...composition,props:{...inputProps,overlay}},inputProps:{...inputProps,overlay},output:path.join(dir,overlay?'thumbnail_overlay.png':'thumbnail_final.png'),imageFormat:'png',puppeteerInstance:browser});await browser.close({silent:true});})();
