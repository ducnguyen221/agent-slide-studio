#!/usr/bin/env python3
"""Render classified catalogue and original, icon-rich infographic examples. No network requests.
Uses local fonts without redistributing them. PNG/SVG are previews, not native PowerPoint SmartArt.
"""
from __future__ import annotations
import os, sys, json, math, html, argparse, importlib.util
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import cairosvg
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
N='#0A192F';B='#2563EB';T='#0F766E';G='#15803D';O='#C2410C';V='#7C3AED';GRAY='#475569';LINE='#CBD5E1';BG='#F8FAFC'
FONT=next((p for p in [os.getenv('AIA_FONT',''),'/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf','C:/Windows/Fonts/arial.ttf'] if p and Path(p).exists()),None)
if not FONT: raise SystemExit('Đặt AIA_FONT tới font hỗ trợ tiếng Việt để dựng ảnh. Không phân phối font trong gói.')
BOLD=FONT.replace('Regular','Bold')
if not Path(BOLD).is_file():BOLD=FONT

def ff(size,bold=False):return ImageFont.truetype(BOLD if bold else FONT,int(size))
def split(s,width,size=32,bold=False):
 f=ff(size,bold);out=[];line=''
 for w in str(s).split():
  cand=(line+' '+w).strip()
  if f.getlength(cand)>width and line:out.append(line);line=w
  else:line=cand
 if line:out.append(line)
 return out

class SVG:
 def __init__(self):
  self.p=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">',
  '''<defs>
  <linearGradient id="cardbg" x1="0" x2="1" y2="1"><stop stop-color="#FFFFFF"/><stop offset="1" stop-color="#F1F7FF"/></linearGradient>
  <linearGradient id="hero" x1="0" x2="1" y2="1"><stop stop-color="#163E7A"/><stop offset="1" stop-color="#0A192F"/></linearGradient>
  <linearGradient id="blue" x1="0" x2="1" y2="1"><stop stop-color="#60A5FA"/><stop offset="1" stop-color="#1D4ED8"/></linearGradient>
  <linearGradient id="teal" x1="0" x2="1" y2="1"><stop stop-color="#2DD4BF"/><stop offset="1" stop-color="#0F766E"/></linearGradient>
  <linearGradient id="purple" x1="0" x2="1" y2="1"><stop stop-color="#C4B5FD"/><stop offset="1" stop-color="#6D28D9"/></linearGradient>
  <linearGradient id="amber" x1="0" x2="1" y2="1"><stop stop-color="#FBBF24"/><stop offset="1" stop-color="#C2410C"/></linearGradient>
  </defs>''']
  self.rect(0,0,1600,900,'white','none',0)
 def rect(self,x,y,w,h,fill='white',stroke=LINE,r=20,sw=2,shadow=False):
  if shadow:self.p.append(f'<rect x="{x}" y="{y+7}" width="{w}" height="{h}" rx="{r}" fill="#D9E3F1" opacity="0.45"/>')
  self.p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
 def circle(self,x,y,r,fill='white',stroke='none',sw=2):self.p.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
 def line(self,x1,y1,x2,y2,c=B,sw=4,dash=False,arrow=False):
  self.p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{sw}" stroke-linecap="round"'+(' stroke-dasharray="8 10"' if dash else '')+'/>')
  if arrow:
   a=math.atan2(y2-y1,x2-x1);al=15+sw;wid=9+sw/2
   pts=[(x2,y2),(x2-al*math.cos(a)+wid*math.sin(a),y2-al*math.sin(a)-wid*math.cos(a)),(x2-al*math.cos(a)-wid*math.sin(a),y2-al*math.sin(a)+wid*math.cos(a))]
   self.poly(pts,c,c,1)
 def poly(self,pts,fill='none',stroke=B,sw=3):
  ps=' '.join(f'{x},{y}' for x,y in pts) if not isinstance(pts,str) else pts
  self.p.append(f'<polygon points="{ps}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>')
 def path(self,d,c=B,sw=4,fill='none',opacity=1):self.p.append(f'<path d="{d}" fill="{fill}" stroke="{c}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" opacity="{opacity}"/>')
 def text(self,x,y,s,size=32,c=N,bold=False,anchor='start',width=None):
  rows=split(s,width,size,bold) if width else [s]
  for i,t in enumerate(rows):
   self.p.append(f'<text x="{x}" y="{y+i*size*1.32}" font-family="Noto Sans, Arial, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{c}" text-anchor="{anchor}">{html.escape(str(t))}</text>')
  return len(rows)*size*1.32
 def title(self,r,kind):
  self.text(88,62,f"{r['id']}   /   {kind}",21,T,True)
  self.text(88,132,r['name'],46,N,True)
  self.line(90,166,1510,166,LINE,2)
 def footer(self,r):
  self.line(90,800,1510,800,LINE,2)
  self.text(90,848,r.get('footer','Mẫu cấu trúc • Thay bằng nội dung đã duyệt'),25,GRAY)
  self.text(1510,848,r['id'],25,B,True,'end')
 def badge(self,x,y,n,c=B):
  self.circle(x,y,28,c,'white',4);self.text(x,y+10,n,29,'white',True,'middle')
 def icon(self,kind,x,y,size=100,c=B,disc=True):
  if disc:self.circle(x+size/2,y+size/2,size*.64,'#EFF6FF')
  self.p.append(f'<g transform="translate({x},{y}) scale({size/100})" fill="none" stroke="{c}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round">')
  if kind=='folder':
   self.path('M10 30V19H40L49 28H89V81H10Z',c,4,'#DCEBFF');self.path('M10 38H94L83 88H7Z',c,4,'url(#blue)')
  elif kind=='shield':
   self.path('M50 7L87 24V50C87 69 72 84 50 96C28 84 13 69 13 50V24Z',c,4,'url(#teal)');self.path('M29 50L44 65L72 35','white',7)
  elif kind=='checklist':
   self.rect(19,16,64,78,'white',c,7,4);self.rect(34,7,34,18,'#DBEAFE',c,5,4)
   for yy in [39,59,79]:self.path(f'M28 {yy}l5 5 9-10',c,3);self.line(51,yy,72,yy,c,3)
  elif kind=='gears':
   self.circle(50,50,24,'url(#blue)',c,4);self.circle(50,50,9,'white',c,3)
   for i in range(8):
    a=i*math.pi/4;self.line(50+26*math.cos(a),50+26*math.sin(a),50+37*math.cos(a),50+37*math.sin(a),c,11)
  elif kind=='file':
   self.path('M22 8H65L84 29V93H22Z',c,4,'#EFF6FF');self.path('M65 8V29H84',c,4)
   for yy,ww in [(45,35),(60,38),(75,27)]:self.line(34,yy,34+ww,yy,c,4)
  elif kind=='magnify':
   self.circle(41,40,28,'#DBEAFE',c,5);self.line(61,62,89,90,c,10);self.path('M28 41l10 9 17-21',c,4)
  elif kind=='user':
   self.circle(50,28,18,'url(#blue)',c,2);self.path('M14 89V78C14 60 28 51 50 51C72 51 86 60 86 78V89Z',c,3,'url(#blue)')
  elif kind=='brain':
   self.path('M47 17C32 3 16 16 22 29C6 35 8 53 20 59C13 73 24 91 40 86L49 79V22M53 17C68 3 84 16 78 29C94 35 92 53 80 59C87 73 76 91 60 86L51 79V22',c,5,'#DBEAFE')
   self.path('M25 34L38 46L25 60M76 34L62 46L77 62M37 46L43 67M62 46L56 69',c,3)
  elif kind=='terminal':
   self.rect(8,18,84,69,'url(#hero)',c,8,4);self.line(9,35,91,35,'#64748B',3)
   for xx in [21,33,45]:self.circle(xx,27,2,'#67E8F9')
   self.path('M25 49L37 61L25 73','#67E8F9',5);self.line(48,73,68,73,'#67E8F9',5)
  elif kind=='book':
   self.path('M49 25C36 13 17 15 8 19V84C24 79 40 83 49 91C58 83 76 79 92 84V19C78 13 62 16 49 25Z',c,4,'#EFF6FF');self.line(49,25,49,88,c,4)
   for yy in [37,50,63]:self.line(19,yy,37,yy,c,3);self.line(62,yy,81,yy,c,3)
  elif kind=='chart':
   self.line(12,87,91,87,c,4);self.rect(20,54,13,32,'url(#blue)','none',3);self.rect(44,40,13,46,'url(#teal)','none',3);self.rect(69,19,13,67,'url(#blue)','none',3);self.path('M20 38L43 27L56 31L83 7',c,4)
  elif kind=='target':
   for rad in [38,25,11]:self.circle(49,53,rad,'none',c,4)
   self.line(49,53,89,12,c,6);self.path('M75 11H90V27',c,4)
  elif kind=='sync':
   self.path('M14 49C12 17 65 3 84 28',c,6);self.path('M69 28H85V11',c,5);self.path('M87 53C91 84 35 99 15 73',c,6);self.path('M30 73H14V90',c,5)
  elif kind=='rocket':
   self.path('M25 63C34 39 48 15 84 10C84 42 63 68 43 77Z',c,4,'#DBEAFE');self.circle(64,32,10,'white',c,4);self.path('M27 51L11 53L7 79L31 68M52 73L49 91L26 96L35 72',c,4,'#EFF6FF');self.path('M21 78L10 90M30 86L21 96',O,5)
  elif kind=='database':
   self.path('M15 22V78C15 99 85 99 85 78V22',c,4,'#DBEAFE');self.p.append(f'<ellipse cx="50" cy="22" rx="35" ry="14" fill="#BFDBFE" stroke="{c}" stroke-width="4"/>');self.path('M15 47C15 66 85 66 85 47M15 70C15 88 85 88 85 70',c,4)
  else:self.path('M20 50L42 73L82 24',c,8)
  self.p.append('</g>')
 def finish(self):self.p.append('</svg>');return '\n'.join(self.p)

# Icons and spacing are purposeful, not illustrations of real products.
def rich(r):
 s=SVG();s.title(r,'INFOGRAPHIC MINH HỌA');p=r['pattern'];h=r['headings'];d=r['descriptions']
 def card(x,y,w,hh,label,desc,ic,c=B,num=None,vertical=False):
  s.rect(x,y,w,hh,'url(#cardbg)',c,24,2,True)
  if num is not None:s.badge(x+36,y+12,num,c)
  if vertical:
   sz=94 if w>250 else 78;s.icon(ic,x+(w-sz)/2,y+54,sz,c)
   s.text(x+w/2,y+193 if w>250 else y+170,label,34,c,True,'middle',w-34)
   s.text(x+w/2,y+256 if w>250 else y+235,desc,30,N,False,'middle',w-35)
  else:
   sz=76;s.icon(ic,x+32,y+(hh-sz)/2,sz,c)
   s.text(x+135,y+58,label,34,c,True,width=w-155)
   s.text(x+135,y+110,desc,30,N,width=w-160)
 if p=='cycle_gate':
  # closed loop around explicit approval hub; four arrows not external paragraphs
  s.path('M985 300C1150 309 1220 355 1220 414',B,7);s.line(1220,393,1220,415,B,6,arrow=True)
  s.path('M1220 584C1206 679 1106 702 984 702',T,7);s.line(1007,702,984,702,T,6,arrow=True)
  s.path('M613 702C420 702 355 655 355 583',V,7);s.line(355,606,355,583,V,6,arrow=True)
  s.path('M355 414C355 340 445 300 610 300',G,7);s.line(587,300,610,300,G,6,arrow=True)
  card(578,207,440,185,h[0],d[0],'checklist',G,1)
  card(1020,414,480,169,h[1],d[1],'terminal',T,2)
  card(578,611,440,168,h[2],d[2],'magnify',B,3)
  card(90,414,480,169,h[3],d[3],'sync',V,4)
  s.icon('shield',739,424,112,T);s.text(795,573,'Kiểm duyệt',34,N,True,'middle')
 elif p in ('illustrated_steps','approval_steps'):
  n=len(h);w=310 if n==4 else 249;gap=46 if n==4 else 39;total=n*w+(n-1)*gap;x0=(1600-total)/2
  icons=['folder','shield','book','magnify'] if n==4 else ['magnify','file','shield','terminal','checklist']
  cols=[B,T,V,G] if n==4 else [B,B,O,T,G]
  for i in range(n):
   x=x0+i*(w+gap);card(x,305,w,406,h[i],d[i],icons[i],cols[i],i+1,True)
   if i<n-1:s.line(x+w+8,498,x+w+gap-8,498,cols[i],5,arrow=True)
  s.text(800,236,r['hero'],35,N,True,'middle')
 elif p=='three_stages':
  cols=[B,T,O];ics=['folder','book','rocket']
  for i in range(3):
   x=150+i*446;y=350-i*55
   card(x,y,408,370,h[i],d[i],ics[i],cols[i],i+1,True)
   s.rect(x-8,y+378,424,31,cols[i],'none',9)
   if i<2:s.line(x+416,y+210,x+439,y+190,cols[i],5,arrow=True)
  s.text(800,223,r['hero'],35,N,True,'middle')
 elif p=='document_flow':
  positions=[140,611,1082];cols=[B,T,V];ics=['folder','gears','chart']
  for i,x in enumerate(positions):
   s.rect(x,300,375,405,'url(#cardbg)',cols[i],25,2,True)
   s.icon(ics[i],x+124,350,125,cols[i]);s.text(x+187,556,h[i],37,cols[i],True,'middle');s.text(x+187,613,d[i],32,N,False,'middle',330)
   if i<2:s.line(x+388,499,x+452,499,cols[i],6,arrow=True)
  s.text(800,229,r['hero'],35,N,True,'middle')
 elif p=='handoff':
  s.text(800,229,r['hero'],35,N,True,'middle')
  for yy,lab,ic,col in [(292,'Con người','user',B),(523,'AI hỗ trợ','brain',T)]:
   s.rect(100,yy,1400,191,'#F8FAFC',LINE,25);s.icon(ic,139,yy+40,81,col);s.text(177,yy+157,lab,28,col,True,'middle')
  xy=[(334,310),(628,543),(925,310),(1216,543)]
  for i,(x,y) in enumerate(xy):
   s.rect(x,y,253,144,'white',B if i%2==0 else T,18,2,True);s.badge(x+25,y+6,i+1,B if i%2==0 else T)
   s.text(x+126,y+55,h[i],30,N,True,'middle',225);s.text(x+126,y+108,d[i],27,GRAY,False,'middle',220)
  s.path('M588 388H606V605H622',B,4);s.line(610,605,622,605,B,4,arrow=True)
  s.path('M882 605H903V388H919',T,4);s.line(907,388,919,388,T,4,arrow=True)
  s.path('M1180 388H1198V605H1210',B,4);s.line(1200,605,1210,605,B,4,arrow=True)
 elif p=='pillars':
  s.poly([(103,302),(800,194),(1497,302)],'url(#hero)',B,3);s.rect(104,302,1393,52,'url(#hero)',B,8)
  s.text(800,305,r['hero'],34,'white',True,'middle')
  cols=[B,T,G,B,V];ics=['folder','shield','book','terminal','checklist']
  for i in range(5):
   x=141+i*271;s.rect(x,389,235,315,'url(#cardbg)',cols[i],22,2,True)
   s.rect(x-6,375,247,22,cols[i],'none',9);s.rect(x-6,695,247,25,cols[i],'none',9)
   s.icon(ics[i],x+71,429,93,cols[i]);s.text(x+117,572,h[i],33,cols[i],True,'middle')
   s.text(x+117,621,d[i],28,N,False,'middle',205)
  s.rect(105,725,1390,45,'#EFF6FF',LINE,11);s.text(800,756,'Không gian làm việc có tổ chức',28,N,True,'middle')
 elif p=='illustrated_layers':
  colors=[B,T,V];icons=['user','gears','database']
  for i in range(3):
   yy=229+i*182;s.rect(147,yy,1306,148,'url(#cardbg)',colors[i],23,2,True)
   s.badge(180,yy+15,i+1,colors[i]);s.icon(icons[i],218,yy+28,87,colors[i]);s.text(360,yy+56,h[i],37,colors[i],True);s.text(360,yy+110,d[i],34,N)
   if i<2:s.line(800,yy+151,800,yy+176,colors[i],5,arrow=True)
 elif p=='maturity':
  cols=[T,B,V,G];ics=['file','user','shield','gears']
  s.rect(136,198,1328,73,'#EFF6FF',LINE,18);s.icon('shield',164,213,41,T,False);s.text(236,247,'Cơ chế giám sát đi cùng năng lực',32,N,True)
  for i in range(4):
   x=122+i*346;yy=438-i*43;hh=319+i*43
   s.rect(x,yy,314,hh,'url(#cardbg)',cols[i],22,2,True);s.badge(x+157,yy+4,i+1,cols[i])
   s.icon(ics[i],x+118,yy+52,78,cols[i]);s.text(x+157,yy+181,h[i],34,cols[i],True,'middle')
   s.text(x+157,yy+231,d[i],29,N,False,'middle',275)
 elif p=='illustrated_hub':
  for xx,yy in [(348,350),(1243,350),(800,663)]:s.line(800,462,xx,yy,B,4)
  s.circle(800,450,143,'#EFF6FF',B,3);s.circle(800,450,120,'url(#hero)',B,2);s.icon('brain',755,373,90,'#67E8F9',False);s.text(800,509,r['hero'],36,'white',True,'middle')
  for x,y,hh,dd,ic,c in [(105,261,h[0],d[0],'checklist',B),(1040,261,h[1],d[1],'book',T),(572,624,h[2],d[2],'terminal',V)]:
   card(x,y,450,151,hh,dd,ic,c)
 elif p=='before_after':
  s.text(800,227,r['hero'],34,N,True,'middle')
  for x,col,label,desc in [(130,GRAY,h[0],d[0]),(922,T,h[1],d[1])]:
   s.rect(x,296,545,441,'url(#cardbg)',col,26,2,True);s.text(x+272,358,label,39,col,True,'middle');s.text(x+272,661,desc,31,N,False,'middle',440)
  for x,y in [(215,422),(413,456),(322,531)]:s.icon('file',x,y,73,GRAY,False)
  s.icon('folder',1032,448,115,B);s.icon('shield',1240,448,115,T)
  s.line(703,510,893,510,B,10,arrow=True);s.text(798,458,'Chuẩn hóa',31,B,True,'middle')
 elif p=='four_cards':
  cols=[B,T,V,G];ics=['book','checklist','terminal','magnify']
  for i in range(4):
   x=118+(i%2)*705;y=271+(i//2)*238
   card(x,y,660,202,h[i],d[i],ics[i],cols[i],i+1)
  s.text(800,225,r['hero'],34,N,True,'middle')
 else:raise ValueError(p)
 s.footer(r);return s.finish()

def structural(r):
 s=SVG();s.title(r,'BỐ CỤC CẤU TRÚC');p=r['pattern']
 def box(x,y,w,h,lab,c=B):
  s.rect(x,y,w,h,'#F8FAFC',c,18);s.text(x+w/2,y+h/2+10,lab,30,c,True,'middle',w-24)
 if p=='agenda':
  s.text(800,255,'Câu hỏi của chương',38,N,True,'middle')
  for i,lab in enumerate(['Hiểu đúng','Chọn cách','Thử làm','Rút kinh nghiệm']):
   x=255+(i%2)*570;y=317+(i//2)*176;box(x,y,520,145,lab,B if i%2==0 else T)
 elif p=='formula':
  s.rect(249,265,1102,166,'#EFF6FF',B,24);s.text(800,365,'Lợi nhuận = Doanh thu − Chi phí',46,B,True,'middle')
  for x,label,desc in [(147,'Lợi nhuận','Kết quả còn lại'),(630,'Doanh thu','Giá trị tạo ra'),(1113,'Chi phí','Nguồn lực sử dụng')]:
   s.line(x+170,431,x+170,511,T,3);box(x,532,350,155,label,T);s.text(x+175,740,desc,25,GRAY,False,'middle')
 elif p=='persona':
  s.rect(140,254,450,471,'#EFF6FF',B,26);s.icon('user',289,304,151,B);s.text(365,541,'Nhân viên mới',34,B,True,'middle');s.text(365,605,'Chân dung minh họa',26,GRAY,False,'middle')
  for i,(lab,desc) in enumerate([('Mục tiêu','Làm đúng quy trình'),('Trở ngại','Chưa rõ bước xử lý'),('Hỗ trợ','Ví dụ và hướng dẫn')]):
   x=655;y=255+i*160;s.rect(x,y,781,137,'white',T,18);s.text(x+35,y+47,lab,30,T,True);s.text(x+35,y+98,desc,31,N)
 elif p=='tradeoff':
  s.line(798,365,798,670,B,8);s.line(370,364,1230,364,B,8);s.poly([(734,719),(800,660),(866,719)],'#DBEAFE',B,3)
  for xx,lab,desc in [(378,'Tốc độ','Thời gian xử lý'),(1228,'Kiểm soát','Mức kiểm tra')]:
   s.line(xx,371,xx,432,T,4);box(xx-224,435,448,177,lab,T);s.text(xx,649,desc,28,GRAY,False,'middle')
  s.text(800,245,'Cân nhắc theo rủi ro',37,N,True,'middle')
 elif p=='scorecard':
  x=175;y=255;widths=[420,420,420];rows=[['Tiêu chí','Phương án A','Phương án B'],['Phù hợp','Cần xác minh','Cần xác minh'],['Chi phí','Cần xác minh','Cần xác minh'],['Kiểm soát','Cần xác minh','Cần xác minh']]
  for i,row in enumerate(rows):
   for j,t in enumerate(row):
    xx=x+sum(widths[:j]);s.rect(xx,y+i*110,widths[j],110,'#EFF6FF' if i==0 else 'white',LINE,0);s.text(xx+widths[j]/2,y+i*110+65,t,29,B if i==0 else N,i==0,'middle')
 elif p=='gates':
  for i,(x,lab) in enumerate([(100,'Chuẩn bị'),(651,'Phê duyệt'),(1202,'Triển khai')]):box(x,359,301,196,lab,B)
  for x,lab in [(512,'Đủ?'),(1063,'Duyệt?')]:
   s.poly([(x,392),(x+69,460),(x,528),(x-69,460)],'#FFF7ED',O,3);s.text(x,470,lab,28,O,True,'middle')
   s.line(x-111,460,x-75,460,B,4,arrow=True);s.line(x+73,460,x+128,460,B,4,arrow=True);s.line(x,534,x,630,O,3,arrow=True)
   s.text(x,677,'Bổ sung',28,O,True,'middle')
  s.text(800,257,'Điểm dừng có điều kiện',37,N,True,'middle')
 elif p=='boundary':
  s.rect(135,255,836,455,'#EFF6FF',B,25);s.text(553,320,'Trong phạm vi cho phép',36,B,True,'middle')
  for i,lab in enumerate(['Đọc','Soạn nháp','Kiểm tra']):box(180+i*255,394,236,202,lab,T)
  box(1110,326,340,130,'Cần phê duyệt',O);box(1110,525,340,130,'Gửi ra ngoài',GRAY)
  s.line(980,414,1100,414,O,5,arrow=True);s.line(1280,466,1280,514,O,5,arrow=True)
 elif p=='waterfall':
  s.line(190,696,1390,696,GRAY,3)
  for x,y,hh,col,lab in [(260,431,263,B,'Đầu kỳ'),(575,313,118,T,'Tăng'),(890,313,76,O,'Giảm'),(1205,389,305,B,'Cuối kỳ')]:
   s.rect(x-72,y,144,hh,col,'none',5);s.text(x,750,lab,29,N,True,'middle')
  s.line(332,431,503,431,GRAY,2,True);s.line(647,313,818,313,GRAY,2,True);s.line(962,389,1133,389,GRAY,2,True)
  s.text(800,250,'Minh họa, chưa gắn số liệu',32,GRAY,False,'middle')
 elif p=='drivers':
  box(541,262,518,157,'Doanh thu',B)
  s.path('M800 420V474H411V532',T,4);s.path('M800 474H1189V532',T,4)
  box(184,537,454,154,'Số lượng',T);box(962,537,454,154,'Đơn giá',T)
  s.text(800,759,'Doanh thu = Số lượng × Đơn giá',32,N,True,'middle')
 elif p=='mistakes':
  for i,(a,b) in enumerate([('Quá nhiều chữ','Giữ ý chính'),('Thiếu lề','Tăng khoảng trống'),('Mũi tên rối','Giữ một hướng đọc')]):
   yy=277+i*148;box(185,yy,490,121,a,GRAY);box(923,yy,490,121,b,T);s.line(711,yy+61,889,yy+61,B,5,arrow=True)
 elif p=='teach':
  for i,(lab,desc) in enumerate([('Kiến thức','Một nguyên lý'),('Minh họa','Một ví dụ'),('Thực hành','Một nhiệm vụ')]):
   x=154+i*450;s.rect(x,320,393,334,'#F8FAFC',B,20);s.text(x+196,433,lab,39,B,True,'middle');s.text(x+196,513,desc,32,N,False,'middle')
   if i<2:s.line(x+405,478,x+439,478,B,5,arrow=True)
 elif p=='actionplan':
  rows=[['Việc cần làm','Phụ trách','Thời điểm','Hoàn thành'],['Chuẩn bị','Vai trò','Mốc','Bằng chứng'],['Thử nghiệm','Vai trò','Mốc','Bằng chứng'],['Đánh giá','Vai trò','Mốc','Bằng chứng']]
  for i,row in enumerate(rows):
   for j,txt in enumerate(row):
    x=130+j*335;y=280+i*104;s.rect(x,y,335,104,'#EFF6FF' if i==0 else 'white',LINE,0);s.text(x+167,y+64,txt,27,B if i==0 else N,i==0,'middle')
 else:raise ValueError(p)
 s.footer(r);return s.finish()

def save_svg(root,r,svg,folder):
 d=root/'previews'/folder;d.mkdir(parents=True,exist_ok=True)
 (d/f"{r['id']}.svg").write_text(svg,encoding='utf-8')
 cairosvg.svg2png(bytestring=svg.encode('utf-8'),write_to=str(d/f"{r['id']}.png"))

def group_sheet(root,g,byid):
 image=Image.new('RGB',(3840,2160),BG);d=ImageDraw.Draw(image)
 d.rounded_rectangle((120,74,332,157),radius=25,fill=g['color']);d.text((155,85),g['id'],font=ff(46,True),fill='white')
 title=g['name'];fsize=69
 while ff(fsize,True).getlength(title)>3300:fsize-=1
 d.text((374,73),title,font=ff(fsize,True),fill=N)
 d.text((124,186),g['subtitle']+'  ·  6 mẫu riêng 16:9  ·  Chọn mã để giao việc',font=ff(35),fill=GRAY)
 for k,id in enumerate(g['members']):
  r=byid[id];x=120+(k%3)*1224;y=304+(k//3)*876
  # labels above each true 16:9 thumbnail
  d.rounded_rectangle((x,y,x+123,y+61),radius=16,fill=g['color']);d.text((x+20,y+8),id,font=ff(32,True),fill='white')
  size=40
  while ff(size,True).getlength(r['name'])>992:size-=1
  d.text((x+145,y+4),r['name'],font=ff(size,True),fill=N)
  im=Image.open(root/r['preview_png']).convert('RGB').resize((1152,648),Image.Resampling.LANCZOS)
  image.paste(im,(x,y+84));d.rectangle((x-1,y+83,x+1152,y+732),outline=LINE,width=3)
  hint=('Cấu trúc nền: '+', '.join(r['base_layouts'])) if id.startswith('I') else 'Quan hệ: '+r['topology'].replace('-',' ')
  d.text((x+5,y+751),hint,font=ff(29),fill=GRAY)
 d.line((120,2050,3720,2050),fill=LINE,width=2)
 d.text((124,2080),'Bảng chọn mẫu • Mở từng mã để đọc nội dung đầy đủ • Mỗi mẫu triển khai thành một slide riêng',font=ff(32),fill=GRAY)
 d.text((3687,2080),'AIA',anchor='ra',font=ff(32,True),fill=g['color'])
 out=root/'previews/groups';out.mkdir(parents=True,exist_ok=True);image.save(out/(g['id']+'.png'),optimize=True)

def gallery(root,groups,allr):
 # Inline metadata supports file:// with no fetch and no remote fonts.
 opts=''.join(f'<option value="{g["id"]}">{g["id"]} · {html.escape(g["name"])}</option>' for g in groups)
 labels={'mo-dau':'Mở đầu','dinh-huong':'Định hướng','giai-thich':'Giải thích','tong-hop':'Tổng hợp','huong-dan':'Hướng dẫn','to-chuc':'Tổ chức','so-sanh':'So sánh','quyet-dinh':'Quyết định','quan-tri':'Quản trị','chung-minh':'Chứng minh','phan-tich':'Phân tích','kham-pha':'Khám phá','thuc-hanh':'Thực hành','ap-dung':'Áp dụng','dinh-vi':'Định vị'}
 intents=sorted(set(x for r in allr for x in r['intent']));tops=sorted(set(r['topology'] for r in allr))
 iopts=''.join(f'<option value="{x}">{labels.get(x,x)}</option>' for x in intents)
 topts=''.join(f'<option value="{x}">{x.replace("-"," ")}</option>' for x in tops)
 boards=''.join(f'<article class="board" data-group="{g["id"]}"><h2>{g["id"]} · {html.escape(g["name"])}</h2><a href="groups/{g["id"]}.png"><img src="groups/{g["id"]}.png" alt="Bảng sáu mẫu thuộc {html.escape(g["name"])}" loading="lazy" width="3840" height="2160"></a></article>' for g in groups)
 cards=[]
 for r in allr:
  png=r['preview_png'].replace('previews/','');svg=r['preview_svg'].replace('previews/','');lab='Infographic minh họa' if r['representation']=='illustrated' else 'Sơ đồ cấu trúc'
  search=' '.join([r['id'],r['name'],r['home_group'],r['topology'],lab,*r['intent']])
  cards.append(f'''<article class="sample" data-group="{r['home_group']}" data-rep="{r['representation']}" data-intent="{' '.join(r['intent'])}" data-topology="{r['topology']}" data-phase="{' '.join(r['deck_phase'])}" data-search="{html.escape(search)}"><p class="kicker">{r['home_group']} · {lab}</p><h2>{r['id']} · {html.escape(r['name'])}</h2><a href="{png}"><img src="{png}" alt="{html.escape(r['name'])}" loading="lazy" width="1600" height="900"></a><p>{html.escape(r['purpose'])}</p><div class="links"><a href="../{r['spec_path']}">Đặc tả Markdown</a><a href="{png}">Ảnh PNG</a><a href="{svg}">Ảnh SVG</a></div></article>''')
 text='''<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Agent Slide Studio · Danh mục bố cục</title><style>
*{box-sizing:border-box}body{margin:0;color:#0a192f;background:#f8fafc;font-family:Arial,sans-serif}header{padding:38px 5%;background:white;border-bottom:1px solid #cbd5e1}h1{font-size:34px;max-width:1100px;line-height:1.25}p{line-height:1.65;color:#475569}header p{max-width:1160px}a{color:#1d4ed8}h2{font-size:20px;line-height:1.4}select,input,button{font:inherit;padding:12px;border:1px solid #94a3b8;border-radius:8px;background:white;color:#0a192f}button{cursor:pointer}button.active{background:#1d4ed8;color:white;border-color:#1d4ed8}.bar{display:flex;flex-wrap:wrap;gap:12px;margin-top:18px}label{display:flex;flex-direction:column;gap:6px;font-size:14px}input{min-width:300px}main{padding:22px 5% 40px}#samples{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:24px}.sample,.board{padding:20px;background:white;border:1px solid #cbd5e1;border-radius:16px}.board{max-width:1550px;margin:0 auto 30px}.sample img,.board img{width:100%;height:auto;display:block;border:1px solid #e2e8f0}.kicker{font-size:12px;color:#0f766e;font-weight:bold}.links{display:flex;gap:14px;flex-wrap:wrap}footer{padding:24px 5%}.hidden,[hidden]{display:none!important}.count{padding:0 5%;font-weight:bold}.notice{background:#eff6ff;border-left:4px solid #2563eb;padding:15px}
</style><header><p class="kicker">AGENT SLIDE STUDIO · v2.1.0</p><h1>Chọn bố cục theo mục đích, không theo số trang</h1><p>48 bố cục cấu trúc (L01–L48) và 12 mẫu infographic có minh họa, biểu tượng, nội dung ngắn (I01–I12). Mỗi mẫu là một slide 16:9 riêng. Chín nhóm chính; G09 có hai nhánh A/B.</p><p><a href="../archetypes/CATALOG.md">Danh mục Markdown</a> · <a href="../taxonomy/README.md">Cách phân loại</a> · <a href="../presentations/INDEX.md">Kịch bản bài thuyết trình</a></p>
<div class="bar"><button id="viewBoards" class="active">Xem bảng theo nhóm</button><button id="viewSamples">Lọc từng mẫu</button><button id="reset">Xóa bộ lọc</button></div>
<div class="bar"><label>Nhóm<select id="group"><option value="">Tất cả nhóm</option><option value="G09">G09 · Tất cả infographic minh họa</option>'''+opts+'''</select></label><label>Loại mẫu<select id="rep"><option value="">Tất cả</option><option value="structural">Sơ đồ cấu trúc</option><option value="illustrated">Infographic minh họa</option></select></label><label>Mục đích<select id="intent"><option value="">Tất cả</option>'''+iopts+'''</select></label><label>Quan hệ<select id="topology"><option value="">Tất cả</option>'''+topts+'''</select></label><label>Vị trí trong bài<select id="phase"><option value="">Tất cả</option><option value="open">Mở đầu</option><option value="explain">Giải thích</option><option value="evidence">Bằng chứng</option><option value="apply">Ứng dụng</option><option value="practice">Thực hành</option><option value="close">Kết thúc</option></select></label><label>Tìm tên hoặc mã<input id="q" type="search" placeholder="Ví dụ: I01, vòng lặp, kiến trúc"></label></div><p class="notice">Các tiêu chí được kết hợp đồng thời. Bảng nhóm dùng để chọn mẫu; nhấn hình để xem đầy đủ. Các mẫu là minh họa thiết kế, không phải slide PPTX/SmartArt có sẵn.</p></header><p id="count" class="count"></p><main><section id="boards">'''+boards+'''</section><section id="samples" hidden>'''+''.join(cards)+'''</section></main><footer>Hoạt động ngoại tuyến · Không tải font, thư viện hoặc dữ liệu từ mạng · Mã cũ được giữ nguyên</footer><script>
const $=s=>document.querySelector(s), controls=['group','rep','intent','topology','phase','q'];let mode='boards';
function norm(s){return s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[đĐ]/g,'d').toLowerCase()}
function groupMatch(g,x){return !g||x===g||(g==='G09'&&x.startsWith('G09'))}
function update(){const v=Object.fromEntries(controls.map(x=>[x,$('#'+x).value]));let count=0;document.querySelectorAll('.sample').forEach(c=>{const ok=groupMatch(v.group,c.dataset.group)&&(!v.rep||v.rep===c.dataset.rep)&&(!v.intent||c.dataset.intent.split(' ').includes(v.intent))&&(!v.topology||c.dataset.topology===v.topology)&&(!v.phase||c.dataset.phase.split(' ').includes(v.phase))&&(!v.q||norm(c.dataset.search).includes(norm(v.q)));c.hidden=!ok;if(ok)count++});let boards=0;document.querySelectorAll('.board').forEach(c=>{const ok=groupMatch(v.group,c.dataset.group);c.hidden=!ok;if(ok)boards++});$('#boards').hidden=mode!=='boards';$('#samples').hidden=mode!=='samples';$('#viewBoards').classList.toggle('active',mode==='boards');$('#viewSamples').classList.toggle('active',mode==='samples');$('#count').textContent=mode==='boards'?boards+' bảng nhóm · Mỗi bảng sáu mẫu':count+' mẫu phù hợp';}
controls.forEach(id=>$('#'+id).addEventListener(id==='q'?'input':'change',()=>{if(id!=='group')mode='samples';update()}));$('#viewBoards').onclick=()=>{mode='boards';controls.filter(x=>x!=='group').forEach(x=>$('#'+x).value='');update()};$('#viewSamples').onclick=()=>{mode='samples';update()};$('#reset').onclick=()=>{controls.forEach(x=>$('#'+x).value='');update()};update();
</script></html>'''
 (root/'previews/index.html').write_text(text,encoding='utf-8')

def main():
 parser=argparse.ArgumentParser();parser.add_argument('root',nargs='?',type=Path,default=ROOT);parser.add_argument('--reuse-existing',action='store_true');args=parser.parse_args();root=args.root.resolve()
 reg=json.loads((root/'archetypes/registry.json').read_text());inf=json.loads((root/'infographics/registry.json').read_text());groups=json.loads((root/'taxonomy/groups.json').read_text());byid={r['id']:r for r in reg+inf}
 legacy=None
 for r in reg:
  if args.reuse_existing and (root/r['preview_png']).is_file() and int(r['id'][1:])<=36:continue
  if int(r['id'][1:])<=36:
   if legacy is None:
    spec=importlib.util.spec_from_file_location('aia_legacy_renderer',root/'scripts/render_previews.py');legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
   svg=legacy.draw_layout(r)
  else:svg=structural(r)
  save_svg(root,r,svg,'layouts')
 for r in inf:save_svg(root,r,rich(r),'infographics')
 for g in groups:group_sheet(root,g,byid)
 gallery(root,groups,reg+inf)
 print(json.dumps({'structural':len(reg),'illustrated':len(inf),'boards':len(groups),'gallery':'previews/index.html'}))
if __name__=='__main__':main()
