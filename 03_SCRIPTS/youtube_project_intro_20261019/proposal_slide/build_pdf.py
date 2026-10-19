from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import qrcode,fitz,json
P=Path(__file__).resolve().parent; R=P.parents[2]; OUT=R/'output/pdf';OUT.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('JP','/Library/Fonts/Arial Unicode.ttf'))
W,H=1600,900
pdf=OUT/'madogiwa_ai_video_one_slide_v2.pdf';c=canvas.Canvas(str(pdf),pagesize=(W,H));c.setTitle('窓際族物語の作品・制作体制・AI動画制作');c.setAuthor('Madogiwa Multimedia Universe')
ink='#152B40';teal='#007E86';muted='#526779'
def text(s,x,y,size=22,color=ink):
 c.setFillColor(HexColor(color));c.setFont('JP',size);c.drawString(x,H-y-size,s)
def line(x,y,w):
 c.setStrokeColor(HexColor('#CBD8DF'));c.setLineWidth(1);c.line(x,H-y,x+w,H-y)
def img(path,x,y,w,h):c.drawImage(str(path),x,H-y-h,w,h,preserveAspectRatio=True,anchor='c',mask='auto')
c.setFillColor(HexColor('#FAFCFD'));c.rect(0,0,W,H,fill=1,stroke=0)
text('窓際族物語',50,30,48);text('作品とAI動画制作',365,46,30)
text('漫画発の8人のキャラクターを、実写・イラストが共演する動画へ。短尺のネタ動画からAI技術解説まで展開。',52,101,22,muted)
line(50,145,1500)
text('01  キャラクターを共有',50,164,27,teal)
img(R/'03_SCRIPTS/00_TEMPLATES/characters/character_sobaya_basic_sheet.png',50,213,400,225)
img(R/'03_SCRIPTS/00_TEMPLATES/characters/character_takosan_basic_sheet.png',50,450,400,225)
text('そば屋・たこさんのキャラクターシート',50,685,18,muted)
text('02  AI生成と編集',490,164,27,teal)
text('台本・演出・参照素材',490,223,24)
text('誰が、どこで、何をするかを決める。',490,263,18,muted)
text('顔・体形・声の基準を揃える。',490,290,18,muted)
line(490,336,310)
text('動画生成モデル',490,355,20,teal)
text('Seedance / Wan',490,393,32)
text('参照画像とプロンプトで映像を生成。',490,443,18,muted)
text('仕上がりを確認し、必要な箇所を修正。',490,470,18,muted)
line(490,516,310)
text('編集・仕上げ',490,537,24)
text('Remotion等で字幕・BGM・尺を調整。',490,579,18,muted)
text('縦9:16に編集し、Shortsへ展開。',490,606,18,muted)
text('プロンプト・参照素材も公式サイト公開。',490,654,18,teal)
text('03  実際に制作したShorts',850,164,27,teal)
examples=[('race.jpg','土下座レース篇','パロディCM','https://www.youtube.com/shorts/G4amr7FfMlI'),('news.jpg','ちくわの水揚げ','架空ニュース','https://madogiwa.work/'),('gta.jpg','赤坂GTAパロディ','ゲーム風映像','https://madogiwa.work/')]
for i,(file,title,genre,url) in enumerate(examples):
 x=850+i*234;img(P/'assets'/file,x,213,214,380.444);text(genre,x,610,17,teal);text(title,x,642,21);c.linkURL(url,(x,H-594,x+214,H-213),relative=0)
text('縦動画の実フレームを掲載',850,685,17,muted)
line(50,727,1500)
text('制作体制',50,750,22,teal)
text('制作の中心：そば屋 ＋ たこさん',50,788,23)
text('アドバイザー：福ギュン／無職やめ太郎',50,826,20,muted)
text('提案への応用例',610,750,22,teal)
text('企業・商品のキャラクターで短尺動画を試作。',610,788,21)
text('表現と品質を確認し、連作企画へ展開。',610,826,20,muted)
url='https://www.youtube.com/channel/UCyQtPu94OaiGxFdd2A6bXdw'
qr=qrcode.make(url);qr.save(P/'assets/youtube_channel_qr.png');img(P/'assets/youtube_channel_qr.png',1415,746,130,130)
text('作品を見る',1248,768,23,teal);text('YouTube',1248,807,20);c.linkURL(url,(1235,20,1550,158),relative=0)
c.linkURL('https://madogiwa.work/',(50,190,450,215),relative=0)
c.showPage();c.save()
d=fitz.open(pdf);assert len(d)==1;d[0].get_pixmap(matrix=fitz.Matrix(1,1)).save(str(OUT/'madogiwa_ai_video_one_slide_v2.png'))
(P/'sources_v2.json').write_text(json.dumps({'sourceVideo':'https://www.youtube.com/watch?v=Ju494EYZiBw','channel':url,'shortFrames':[{'file':'race.jpg','source':'03_SCRIPTS/67_madogiwa_super_try_keisha/final_remotion_shorts_9x16.mp4','seconds':3},{'file':'news.jpg','source':'03_SCRIPTS/25_chikuwa_landing_news/final_remotion_shorts_9x16.mp4','seconds':3},{'file':'gta.jpg','source':'03_SCRIPTS/50_sobaya_akasaka_gta_parody/final_remotion_shorts_9x16.mp4','seconds':4}],'note':'サムネイル画像として縦加工済み動画の実フレームを使用。応用例は提案案。'},ensure_ascii=False,indent=2)+'\n')
print(pdf)
