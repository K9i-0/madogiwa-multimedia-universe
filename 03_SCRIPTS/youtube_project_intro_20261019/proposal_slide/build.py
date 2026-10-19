from pathlib import Path
import base64
p=Path(__file__).resolve().parent
root=p.parents[2]
image=base64.b64encode((root/'16_MADOGIWA_STUDIO/public/site/ogp-balcony-20260912.jpg').read_bytes()).decode()
html='''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>窓際族物語｜作品・制作体制・AI動画制作</title>
<style>
*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;background:#e4e8ec;font-family:"Hiragino Kaku Gothic ProN","Yu Gothic",Meiryo,sans-serif;color:#172b40}body{display:flex;align-items:center;justify-content:center}.slide{width:1600px;height:900px;flex-shrink:0;background:#fbfcfd;transform:scale(var(--scale,1));padding:48px 64px;position:relative;overflow:hidden}h1,h2,p{margin:0}header{height:86px}h1{font-size:49px;letter-spacing:1px;font-weight:800}header p{font-size:24px;color:#526273;margin-top:12px}.main{display:grid;grid-template-columns:680px 1fr;gap:48px}.hero{width:680px;height:356px;object-fit:contain;display:block}.caption{font-size:24px;font-weight:700;margin-top:17px;line-height:1.55}.caption small{display:block;font-size:20px;font-weight:400;color:#526273;margin-top:7px}.right h2{font-size:26px;color:#126d78;margin-bottom:12px}.right p{font-size:23px;line-height:1.65}.right .team{margin-top:30px}.right strong{font-weight:750}.roles{margin-top:5px!important;color:#526273;font-size:21px!important}.workflow{margin-top:17px;display:grid;grid-template-columns:216px 1fr;gap:28px;border-top:2px solid #b9cbd0;padding-top:20px}.workflow h2{font-size:26px;color:#126d78;line-height:1.45}.steps{display:grid;grid-template-columns:1fr 1fr 1fr;gap:26px}.step b{display:block;font-size:23px;margin-bottom:9px}.step p{font-size:20px;line-height:1.55;color:#415468}.proposal{font-size:23px;margin-top:23px;padding-top:17px;border-top:1px solid #d8e1e7;line-height:1.55}.proposal strong{color:#126d78;margin-right:18px}footer{position:absolute;left:64px;right:64px;bottom:29px;display:flex;justify-content:space-between;align-items:center;font-size:17px;color:#647281}a{color:#126d78;text-decoration:none}a:hover{text-decoration:underline}footer .links{display:flex;gap:25px}@page{size:1600px 900px;margin:0}@media print{html,body{background:white;width:1600px;height:900px}.slide{transform:none!important;print-color-adjust:exact;-webkit-print-color-adjust:exact}a{color:inherit}}
</style>
<main class="slide" aria-label="窓際族物語の紹介スライド">
<header><h1>窓際族物語の作品とAI動画制作</h1></header>
<div class="main"><section><img class="hero" src="data:image/jpeg;base64,IMAGE" alt="窓際族物語の公式ビジュアル。ベランダでビールを飲むそば屋と仲間たち"><p class="caption">架空のIT企業「アクシデンチュア」の窓際族8人<small>実在のモデルを持つメンバーを、実写とイラストで共演させる。</small></p></section>
<section class="right"><h2>作品展開</h2><p><strong>漫画から始まり、現在は動画が主力。</strong><br>ネタ動画・パロディCMから、AIの技術解説まで。<br>Tシャツ・LINEスタンプ、ゲームの試作にも展開。</p>
<div class="team"><h2>制作体制</h2><p><strong>制作の中心　そば屋 ＋ たこさん</strong></p><p class="roles">アドバイザー　福ギュン／無職やめ太郎</p><p style="margin-top:16px">人が企画・演出・仕上がりを判断し、<br>台本相談・素材生成・編集コードにAIを活用。</p></div></section></div>
<section class="workflow"><h2>制作ノウハウ</h2><div class="steps"><div class="step"><b>01　キャラと演出を決める</b><p>台本と参照画像・声を準備。<br>顔やシルエットの同一性を保つ。</p></div><div class="step"><b>02　映像・音声を作る</b><p>Seedance／Wan等で映像生成。<br>音声も用途に応じて作成・調整。</p></div><div class="step"><b>03　編集し、確認して直す</b><p>字幕・BGM・尺を編集。<br>プロンプトや参照素材をサイト公開。</p></div></div></section>
<p class="proposal"><strong>提案への応用例</strong>企業・商品のキャラクターを使った短尺の紹介動画や連作企画。<br><span style="padding-left:203px">まず1本を試作し、表現・品質を確認してシリーズ化を検討。</span></p>
<footer><span>窓際族物語 / Madogiwa Multimedia Universe</span><span class="links"><a href="https://madogiwa.work/">公式サイト　madogiwa.work ↗</a><a href="https://www.youtube.com/watch?v=Ju494EYZiBw">作品・制作体制の紹介動画 ↗</a></span></footer>
</main><script>function fit(){document.documentElement.style.setProperty('--scale',Math.min(innerWidth/1600,innerHeight/900))}addEventListener('resize',fit);fit()</script>
<!-- 出典: 公開紹介動画 https://www.youtube.com/watch?v=Ju494EYZiBw / 制作ノート https://madogiwa.work/episodes/madogiwa-project-introduction / AI動画制作 https://madogiwa.work/episodes/coding-ai-wan-video-workflow 。画像: 公式OGP ogp-balcony-20260912.jpg。下段の「提案への応用例」は今回の提案案であり、受託実績や効果・納期の保証ではない。 -->
</html>'''.replace('IMAGE',image)
(p/'madogiwa_one_slide.html').write_text(html)
print(p/'madogiwa_one_slide.html')
