from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import pymupdf,zxingcpp
from PIL import Image
P=Path(__file__).resolve().parent;R=P.parents[2];O=R/'output/pdf';A=P/'assets';S=R/'03_SCRIPTS/00_TEMPLATES/characters'
pdfmetrics.registerFont(TTFont('JP','/Library/Fonts/Arial Unicode.ttf'))
W,H=1600,900;url='https://www.youtube.com/channel/UCyQtPu94OaiGxFdd2A6bXdw'
files=[]
def text(s,x,y,size=22,color=None,font='JP'):
 c.setFillColor(HexColor(color or ink));c.setFont(font,size);c.drawString(x,H-y-size,s)
def image(p,x,y,w,h):c.drawImage(str(p),x,H-y-h,w,h,preserveAspectRatio=True,anchor='c',mask='auto')
def rule(y,x=50,w=1500):
 c.setStrokeColor(HexColor(muted));c.setLineWidth(.5);c.line(x,H-y,x+w,H-y)
def sheets(x,y,w,gap=15):
 image(S/'character_sobaya_basic_sheet.png',x,y,w,w*9/16)
 image(S/'character_fukuchan_basic_sheet.png',x,y+w*9/16+gap,w,w*2/3)
def models(x,y):
 image(A/'seed_official.png',x,y,40,40);text('Seedance',x+53,y+2,25);text('ByteDance Seed',x+53,y+36,13,muted)
 image(A/'wan_official.png',x,y+80,40,40);text('Wan',x+53,y+83,25)
def shorts(x,y,w,gap=20):
 for i,(f,t,g) in enumerate([('race.jpg','土下座レース篇','パロディCM'),('news.jpg','ちくわの水揚げ','架空ニュース'),('fukugyun.jpg','福ギュン誕生','キャラクターの物語')]):
  xx=x+i*(w+gap);image(A/f,xx,y,w,w*16/9);text(g,xx,y+w*16/9+15,17,accent);text(t,xx,y+w*16/9+45,20)
def footer(y=752):
 rule(y-20);text('制作  そば屋 ＋ たこさん',50,y,23);text('アドバイザー  福ギュン／無職やめ太郎',50,y+41,20,muted)
 text('提案への応用例',620,y,21,accent);text('企業・商品のキャラで短尺動画を試作。',620,y+37,21);text('表現と品質を確認し、連作企画へ。',620,y+70,20,muted)
 image(A/'youtube_channel_qr.png',1415,y-4,130,130);text('作品を見る',1245,y+18,22,accent);text('YouTube',1245,y+55,20);c.linkURL(url,(1230,10,1550,170))
for kind in ['consulting','venture','studio']:
 bg,ink,muted,accent={'consulting':('#FFFFFF','#142E4D','#5D6F80','#176B9A'),'venture':('#10171C','#F4F7F5','#B5C3C7','#C9F267'),'studio':('#F4F0E8','#252D30','#6F726F','#B34E31')}[kind]
 p=O/f'madogiwa_{kind}_v4.pdf';files.append(p);c=canvas.Canvas(str(p),pagesize=(W,H));c.setTitle('窓際族物語 / '+kind);c.setAuthor('Madogiwa Multimedia Universe');c.setFillColor(HexColor(bg));c.rect(0,0,W,H,fill=1,stroke=0)
 if kind=='consulting':
  text('窓際族物語のAIショート動画制作',50,31,43);text('キャラクター資産・制作工程・作品展開',52,94,24,muted);rule(145)
  text('01  キャラクター資産',50,165,27,accent);sheets(50,216,370);text('そば屋／福ギュンのキャラクターシート',50,698,17,muted)
  text('02  制作工程と使用モデル',470,165,27,accent);text('台本と参照画像・声を準備',470,221,22);text('顔・体形・声の基準を揃える。',470,262,18,muted);models(470,317)
  text('生成結果を確認・修正',470,475,23);text('Remotion等で字幕・BGM・尺を編集。',470,522,18,muted);text('縦9:16でShortsへ展開。',470,553,18,muted);text('プロンプト・参照素材を公開',470,630,22,accent);text('作例と作り方を公式サイトで共有。',470,671,18,muted)
  text('03  制作したShorts',850,165,27,accent);shorts(850,216,214);footer(765)
 elif kind=='venture':
  text('窓際族物語',50,30,51);text('キャラクターを、次のショート動画へ。',50,97,30,accent)
  text('漫画発の8人。実写とイラストが共演するAI制作プロジェクト。',50,150,22,muted)
  shorts(850,45,214)
  sheets(50,218,360,12)
  text('そば屋／福ギュン',50,690,18,muted)
  text('つくる仕組み',455,222,28,accent);text('台本・参照画像・声を揃える',455,278,21);models(455,334)
  text('生成して、確認して、直す。',455,501,23);text('字幕・BGM・尺は編集で仕上げる。',455,548,19,muted);text('縦9:16へ加工してShortsに。',455,581,19,muted)
  text('作り方も公開',850,580,29,accent);text('プロンプト・参照素材を公式サイトで共有。',850,631,23);text('ネタ動画から、AIの技術解説まで展開。',850,673,21,muted);footer(765)
 else:
  text('MADOGIWA / CREATIVE WORKS',50,30,20,accent,font='Helvetica');text('窓際族物語',50,65,48);text('キャラクターと映像を育てる制作プロジェクト',410,83,27)
  rule(150);text('CHARACTERS',50,173,20,accent,font='Helvetica');text('SHORT FILMS',475,173,20,accent,font='Helvetica');text('PRODUCTION',1160,173,20,accent,font='Helvetica')
  sheets(50,220,355,18);text('そば屋／福ギュン',50,695,18,muted);shorts(475,220,205,18)
  text('台本・参照素材を準備',1160,222,23);text('顔・体形・声を継続して保つ。',1160,267,18,muted);models(1160,322)
  text('映像生成と確認・修正',1160,485,23);text('字幕・BGM・尺を編集し、',1160,531,19,muted);text('縦9:16のShortsへ仕上げる。',1160,562,19,muted)
  text('ノウハウを共有',1160,624,23,accent);text('プロンプト・参照素材を公開。',1160,667,18,muted);footer(765)
 c.showPage();c.save();d=pymupdf.open(p);assert len(d)==1;png=p.with_suffix('.png');d[0].get_pixmap().save(png)
 codes=zxingcpp.read_barcodes(Image.open(png));assert any(a.text==url for a in codes)
allpdf=pymupdf.open()
for f in files:
 with pymupdf.open(f) as d:allpdf.insert_pdf(d)
allpdf.save(O/'madogiwa_three_designs_v4.pdf')
print('\n'.join(map(str,files)))
