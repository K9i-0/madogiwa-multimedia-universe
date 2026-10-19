const {chromium}=require(process.cwd()+'/03_SCRIPTS/youtube_3d_character_workflow_20261014/remotion/node_modules/playwright');
(async()=>{const b=await chromium.launch({headless:true,channel:"chrome"});const p=await b.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
for(const [name,url] of [['site','https://madogiwa.work'],['videos_site','https://madogiwa.work/episodes'],['manga_site','https://madogiwa.work/story'],['prompt_site','https://madogiwa.work/episodes/madogiwa-super-try-commute']]){
 await p.goto(url,{waitUntil:'networkidle'});await p.screenshot({path:`03_SCRIPTS/youtube_project_intro_20261019/remotion/public/${name}.png`});require('fs').writeFileSync(`/tmp/mmu_${name}.txt`,await p.locator('body').innerText());
 if(name==='prompt_site'){console.log((await p.locator('body').innerText()).slice(-10000));console.log(await p.locator('button').allTextContents());}
}await b.close()})();
