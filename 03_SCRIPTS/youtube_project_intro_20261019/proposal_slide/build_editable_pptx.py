"""Export approved PDF layout as editable native DrawingML text plus embedded images.
No font binaries are embedded. Meiryo UI resolves on the recipient's system.
"""
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZipFile,ZIP_DEFLATED
import io,json
import pymupdf
from PIL import Image
P=Path(__file__).resolve().parent;R=P.parents[2]; O=R/'output/pptx';O.mkdir(parents=True,exist_ok=True)
source=R/'output/pdf/madogiwa_studio_v5.pdf';doc=pymupdf.open(source);page=doc[0]
A='http://schemas.openxmlformats.org/drawingml/2006/main'; PP='http://schemas.openxmlformats.org/presentationml/2006/main'; RR='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
ns=f'xmlns:a="{A}" xmlns:p="{PP}" xmlns:r="{RR}"'
def xml(s):return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'+s
def emu(x):return round(x*9525)
def xfrm(x,y,w,h):return f'<a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
def rels(items):return xml('<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join(f'<Relationship Id="{i}" Type="{RR}/{typ}" Target="{target}"'+(' TargetMode="External"' if typ=='hyperlink' else '')+'/>' for i,typ,target in items)+'</Relationships>')
def tree():return '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
parts={};shapes=[];rid=[('rId1','slideLayout','../slideLayouts/slideLayout1.xml')];idx=1;count=0
# Original rules, as native slide lines.
for y in [150,745]:
 idx+=1;shapes.append(f'<p:sp><p:nvSpPr><p:cNvPr id="{idx}" name="Separator {idx}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr>{xfrm(50,y,1500,.1)}<a:prstGeom prst="line"><a:avLst/></a:prstGeom><a:ln w="4763"><a:solidFill><a:srgbClr val="6F726F"/></a:solidFill></a:ln></p:spPr></p:sp>')
for b in page.get_text('dict')['blocks']:
 if b['type']==1:
  idx+=1;count+=1;x,y,x2,y2=b['bbox'];ext=b['ext'];data=b['image']
  if b.get('mask'):
   im=Image.open(io.BytesIO(data)).convert('RGBA');im.putalpha(Image.open(io.BytesIO(b['mask'])).convert('L'));out=io.BytesIO();im.save(out,format='PNG');data=out.getvalue();ext='png'
  name=f'image{count}.{ext}';parts['ppt/media/'+name]=data;rel=f'rId{len(rid)+1}';rid.append((rel,'image','../media/'+name))
  shapes.append(f'<p:pic><p:nvPicPr><p:cNvPr id="{idx}" name="Image {count}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr><p:blipFill><a:blip r:embed="{rel}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr>{xfrm(x,y,x2-x,y2-y)}<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>')
 else:
  for line in b['lines']:
   for s in line['spans']:
    idx+=1;x,y,x2,y2=s['bbox'];size=s['size'];txt=s['text'];color=f'{s["color"]:06X}'
    # Widen text boxes within their existing columns to allow font substitution.
    right=1550 if x>=1160 else (1130 if x>=475 else (1125 if x>=410 else 440))
    if y<150:right=1550
    if y>740:right=1200 if x>=620 and x<1200 else (580 if x<620 else 1410)
    width=max(x2-x+20,right-x);height=max(y2-y+10,size*1.8)
    shapes.append(f'<p:sp><p:nvSpPr><p:cNvPr id="{idx}" name="Text {idx}: {escape(txt[:25])}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr>{xfrm(x,y-3,width,height)}<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr wrap="none" lIns="0" tIns="0" rIns="0" bIns="0" anchor="t"><a:noAutofit/></a:bodyPr><a:lstStyle/><a:p><a:pPr/><a:r><a:rPr lang="ja-JP" sz="{round(size*75)}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:latin typeface="Meiryo UI"/><a:ea typeface="Meiryo UI"/><a:cs typeface="Meiryo UI"/></a:rPr><a:t>{escape(txt)}</a:t></a:r><a:endParaRPr lang="ja-JP"/></a:p></p:txBody></p:sp>')
parts['ppt/slides/slide1.xml']=xml(f'<p:sld {ns}><p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="F4F0E8"/></a:solidFill><a:effectLst/></p:bgPr></p:bg><p:spTree>{tree()}{"".join(shapes)}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>')
parts['ppt/slides/_rels/slide1.xml.rels']=rels(rid)
parts['ppt/presentation.xml']=xml(f'<p:presentation {ns}><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:sldIdLst><p:sldId id="256" r:id="rId2"/></p:sldIdLst><p:sldSz cx="15240000" cy="8572500" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>')
parts['ppt/_rels/presentation.xml.rels']=rels([('rId1','slideMaster','slideMasters/slideMaster1.xml'),('rId2','slide','slides/slide1.xml')])
clr='<p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/>'
parts['ppt/slideMasters/slideMaster1.xml']=xml(f'<p:sldMaster {ns}><p:cSld><p:spTree>{tree()}</p:spTree></p:cSld>{clr}<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>')
parts['ppt/slideMasters/_rels/slideMaster1.xml.rels']=rels([('rId1','slideLayout','../slideLayouts/slideLayout1.xml'),('rId2','theme','../theme/theme1.xml')])
parts['ppt/slideLayouts/slideLayout1.xml']=xml(f'<p:sldLayout {ns} type="blank" preserve="1"><p:cSld name="Blank"><p:spTree>{tree()}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>')
parts['ppt/slideLayouts/_rels/slideLayout1.xml.rels']=rels([('rId1','slideMaster','../slideMasters/slideMaster1.xml')])
colors={'dk1':'252D30','lt1':'FFFFFF','dk2':'6F726F','lt2':'F4F0E8','accent1':'B34E31','accent2':'007E86','accent3':'567088','accent4':'9BAAB0','accent5':'C7AA82','accent6':'E2CCB0','hlink':'007E86','folHlink':'B34E31'}
font='<a:latin typeface="Meiryo UI"/><a:ea typeface="Meiryo UI"/><a:cs typeface="Meiryo UI"/>'
fill='<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
parts['ppt/theme/theme1.xml']=xml(f'<a:theme xmlns:a="{A}" name="Madogiwa Meiryo UI"><a:themeElements><a:clrScheme name="Madogiwa">'+''.join(f'<a:{k}><a:srgbClr val="{v}"/></a:{k}>' for k,v in colors.items())+f'</a:clrScheme><a:fontScheme name="Meiryo UI"><a:majorFont>{font}</a:majorFont><a:minorFont>{font}</a:minorFont></a:fontScheme><a:fmtScheme name="Simple"><a:fillStyleLst>{fill*3}</a:fillStyleLst><a:lnStyleLst>'+(' <a:ln w="9525">'+fill+'<a:prstDash val="solid"/></a:ln>')*3+f'</a:lnStyleLst><a:effectStyleLst>'+('<a:effectStyle><a:effectLst/></a:effectStyle>')*3+f'</a:effectStyleLst><a:bgFillStyleLst>{fill*3}</a:bgFillStyleLst></a:fmtScheme></a:themeElements></a:theme>')
parts['_rels/.rels']=rels([('rId1','officeDocument','ppt/presentation.xml')])
types={'ppt/presentation.xml':'presentation.main','ppt/slides/slide1.xml':'slide','ppt/slideMasters/slideMaster1.xml':'slideMaster','ppt/slideLayouts/slideLayout1.xml':'slideLayout'}
parts['[Content_Types].xml']=xml('<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Default Extension="jpeg" ContentType="image/jpeg"/>'+''.join(f'<Override PartName="/{p}" ContentType="application/vnd.openxmlformats-officedocument.presentationml.{t}+xml"/>' for p,t in types.items())+'<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/></Types>')
path=O/'madogiwa_studio_Meiryo_UI_editable.pptx'
with ZipFile(path,'w',ZIP_DEFLATED) as z:
 for p,v in parts.items():z.writestr(p,v)
# Verify package XML and text content without relying on an unavailable local Meiryo UI renderer.
import xml.etree.ElementTree as etree
with ZipFile(path) as z:
 for n in z.namelist():
  if n.endswith(('.xml','.rels')):etree.fromstring(z.read(n))
 root=etree.fromstring(z.read('ppt/slides/slide1.xml'));texts=root.findall('.//{'+A+'}t');assert len(texts)==31,len(texts)
 assert all(t.get('typeface')=='Meiryo UI' for t in root.findall('.//{'+A+'}ea'))
print(json.dumps({'file':str(path),'editableTextBoxes':len(texts),'images':count,'font':'Meiryo UI'},ensure_ascii=False))
