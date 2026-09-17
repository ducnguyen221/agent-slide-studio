#!/usr/bin/env python3
"""Render original layout wireframes; requires CairoSVG and Pillow, not an image-generation service."""
from __future__ import annotations
import argparse, html, json, math, os
from pathlib import Path

NAVY='#0A192F'; BLUE='#2563EB'; TEAL='#0F766E'; GREEN='#15803D'; ORANGE='#F97316'; BORDER='#CBD5E1'; PALE='#EFF6FF'; GRAY='#475569'

def draw_layout(r: dict) -> str:
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">',
           '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#2563EB"/></marker></defs>']
    def rect(x,y,w,h,fill='white',stroke=BORDER,rad=20,sw=2):parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rad}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    def text(x,y,s,size=28,color=NAVY,anchor='start',weight=500):
        parts.append(f'<text x="{x}" y="{y}" font-family="Noto Sans, Arial, sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{html.escape(str(s))}</text>')
    def line(x1,y1,x2,y2,color=BLUE,arrow=False,dashed=False,sw=4):
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"'+(' marker-end="url(#arrow)"' if arrow else '')+(' stroke-dasharray="10 8"' if dashed else '')+'/>')
    def path(d,color=BLUE,arrow=False,fill='none',sw=4):parts.append(f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw}"'+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
    def circle(x,y,r,fill=PALE,stroke=BLUE,sw=3):parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    def poly(points,fill=PALE,stroke=BLUE):parts.append(f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="3"/>')
    def bars(x,y,w,n=3,step=24):
        for i in range(n):rect(x,y+i*step,w*(.95-.12*(i%3)),9,'#CBD5E1','none',4)
    def card(x,y,w,h,label,accent=BLUE,number=None):
        rect(x,y,w,h,stroke=accent)
        if number is not None:
            circle(x+34,y+34,21,accent,accent);text(x+34,y+43,str(number),23,'white','middle',700)
        text(x+w/2,y+58,label,27,accent,'middle',700)
        if h>120:bars(x+26,y+94,w-52,min(3,max(1,int((h-120)/25)+1)))
    p=r['pattern'];rect(0,0,1600,900,'#F8FAFC','none',0)
    if p=='background':
        rect(0,0,1600,900,NAVY,'none',0)
        for k in range(8):path(f'M 0 {370+k*35} C 190 {120+k*55}, 350 {700-k*20}, 570 {760+k*8}', '#0F766E',sw=1.5)
        for k in range(6):
            x=1160+k*45;y=610-k*50
            poly(f'{x},{y} {x+72},{y-38} {x+146},{y} {x+72},{y+42}',fill='none',stroke='#0891B2')
            path(f'M{x},{y} V{y+94} L{x+72},{y+138} L{x+146},{y+94} V{y} M{x+72},{y+42} V{y+138}','#0891B2',sw=2)
        for i in range(15):circle(40+i*17,160+(i*61)%570,3,'#67E8F9','none',0)
        parts.append('</svg>');return '\n'.join(parts)
    text(90,86,f"{r['id']}   /   THƯ VIỆN BỐ CỤC AIA",21,TEAL,weight=700)
    title_size=43 if len(r['name'])<39 else 38
    text(90,150,r['name'],title_size,weight=800)
    line(90,184,1510,184,BORDER,sw=2)
    if p=='cover':
        text(110,370,'THÔNG ĐIỆP',56,weight=800);text(110,445,'TRUNG TÂM',56,BLUE,weight=800);bars(110,510,640,3,32)
        circle(1160,470,170,PALE,BLUE,3);rect(1050,340,220,250,'white',TEAL,26);line(1085,402,1230,402,TEAL,sw=8);bars(1085,450,150,4,32)
    elif p in ('roadmap','process','case','storyboard'):
        n=3 if p in ('case','storyboard') else 4
        ww=360 if n==3 else 300;gap=65 if n==3 else 50;start=(1600-(ww*n+gap*(n-1)))/2
        labs=['Vấn đề','Giải pháp','Tác động'] if p=='case' else ([f'Cảnh {i+1}' for i in range(n)] if p=='storyboard' else [f'Bước {i+1}' for i in range(n)])
        for i in range(n):
            x=start+i*(ww+gap);accent=TEAL if (p=='roadmap' and i==1) else BLUE
            card(x,320,ww,300,labs[i],accent,i+1)
            if p=='storyboard':circle(x+ww/2,505,35,PALE,TEAL)
            else:rect(x+30,558,ww-60,40,PALE,'none',12);text(x+ww/2,586,'Đầu ra',22,TEAL,'middle')
            if i<n-1:line(x+ww+8,465,x+ww+gap-12,465,arrow=True)
    elif p=='anatomy':
        card(115,350,490,260,'Khái niệm gốc',TEAL)
        for i in range(3):
            yy=250+i*155;card(875,yy,550,115,f'Thuộc tính {i+1}')
            path(f'M605,480 H740 V{yy+57} H875',BLUE,False,sw=3)
    elif p=='matrix':
        for i in range(4):card(440+(i%2)*410,255+(i//2)*220,380,195,chr(65+i),[BLUE,TEAL,TEAL,BLUE][i])
        line(365,705,365,240,arrow=True);line(365,705,1290,705,arrow=True)
        text(325,280,'Cao',22,GRAY,'end');text(325,696,'Thấp',22,GRAY,'end');text(430,750,'Trục X: thấp → cao',24,GRAY);text(116,478,'Trục Y',27,TEAL)
    elif p=='comparison':
        for i,lab in enumerate(['Phương án A','Phương án B']):
            x=370+i*555;rect(x,240,520,450,'white',BLUE if i==0 else TEAL);text(x+260,296,lab,30,BLUE if i==0 else TEAL,'middle',700)
            for k in range(3):line(x+25,340+k*110,x+495,340+k*110,BORDER,sw=2);bars(x+35,370+k*105,425,2)
        for k in range(3):text(120,395+k*108,f'Tiêu chí {k+1}',25,GRAY)
    elif p=='layers':
        for i,lab in enumerate(['Con người và quản trị','Nền tảng và năng lực','Dữ liệu và công cụ']):
            yy=240+i*173;rect(220,yy,1160,125,PALE,BLUE);text(800,yy+49,lab,32,BLUE,'middle',700)
            for k in range(3):rect(270+k*365,yy+72,335,28,'white',BORDER,7)
            if i<2:line(800,yy+132,800,yy+165,arrow=True)
    elif p=='exercise':
        card(115,245,780,315,'Đề bài và dữ liệu');card(935,245,545,315,'Sản phẩm cần nộp',TEAL)
        card(115,595,1365,115,'Tiêu chí hoàn thành',TEAL)
    elif p=='bento':
        card(115,250,780,445,'Nguyên lý chính',BLUE)
        card(930,250,545,185,'Ý hỗ trợ 1',TEAL);card(930,465,545,230,'Ý hỗ trợ 2',TEAL)
    elif p=='hub':
        for x,y in [(350,330),(1250,330),(800,675)]:line(800,440,x,y,TEAL,sw=4)
        circle(800,420,118,PALE,BLUE);text(800,431,'LÕI',39,BLUE,'middle',800)
        card(160,245,370,170,'Mô-đun A',TEAL);card(1070,245,370,170,'Mô-đun B',TEAL);card(595,595,410,120,'Mô-đun C',TEAL)
    elif p=='cycle':
        card(155,250,480,170,'1. Quan sát');card(970,250,480,170,'2. Phân tích')
        card(970,540,480,170,'3. Cập nhật có duyệt',ORANGE);card(155,540,480,170,'4. Áp dụng lại',TEAL)
        path('M650,325 Q800,245 950,325',arrow=True);path('M1440,432 Q1510,480 1440,523',arrow=True)
        path('M955,625 Q800,715 650,625',arrow=True);path('M150,530 Q75,470 150,430',arrow=True)
        circle(800,477,62,PALE,TEAL);text(800,488,'Học hỏi',22,TEAL,'middle',700)
    elif p=='document':
        rect(100,230,830,495,NAVY,NAVY,20);text(135,283,'SKILL.md',27,'white',weight=700)
        labs=['name / description','Đầu vào và phạm vi','Các bước thực hiện','Đầu ra và kiểm tra']
        for i in range(4):
            yy=314+i*97;rect(135,yy,755,77,'#12243D',TEAL,10);text(159,yy+43,labs[i],23,'white')
            line(905,yy+39,1014,yy+39,BLUE,dashed=True,sw=3);card(1025,yy-5,465,90,f'Chú giải {i+1}',TEAL)
    elif p=='ui':
        rect(320,250,1000,440,'white',BLUE,18);rect(320,250,1000,55,PALE,BLUE,12)
        rect(345,330,200,330,PALE,BORDER,10);rect(565,330,300,330,'#F5F3FF',BORDER,10);rect(885,330,410,205,PALE,BORDER,10);rect(885,555,410,105,NAVY,NAVY,10)
        for x,y,num in [(430,374,1),(714,374,2),(1085,374,3),(1085,605,4)]:circle(x,y,24,BLUE,BLUE);text(x,y+8,str(num),24,'white','middle',700)
        text(85,349,'Thư mục',25,TEAL);line(200,355,310,355,TEAL,sw=2)
        text(90,470,'Tương tác',25,TEAL);line(220,475,305,475,TEAL,sw=2)
        text(1340,420,'Kết quả',25,TEAL);line(1325,425,1490,425,TEAL,sw=2)
        text(1340,615,'Tác vụ',25,TEAL);line(1325,630,1460,630,TEAL,sw=2)
    elif p=='tree':
        card(610,230,380,100,'Gốc',TEAL)
        line(800,330,800,390);line(420,390,1180,390)
        for x,lab in [(210,'Nhánh A'),(990,'Nhánh B')]:
            line(x+200,390,x+200,430);card(x,430,400,100,lab)
            for xx in [x,x+220]:line(x+200,530,xx+90,590);card(xx,595,180,110,'Nhóm con',TEAL)
    elif p=='stair':
        for i in range(4):
            x=170+i*315;y=560-i*85;rect(x,y,285,160+i*85,PALE,BLUE,12);text(x+142,y+55,f'Mức {i+1}',31,BLUE,'middle',700);bars(x+40,y+88,195,2)
    elif p=='ipo':
        card(100,255,360,180,'Nguồn A',TEAL);card(100,490,360,180,'Nguồn B',TEAL)
        path('M470,345 H520 V455 H575',arrow=True);path('M470,580 H520 V455 H575',arrow=True)
        card(595,330,440,255,'Xử lý',BLUE);line(1055,455,1110,455,arrow=True);card(1130,330,370,255,'Đầu ra',TEAL)
    elif p=='wave':
        for i in range(5):
            x=95+i*290;y=270 if i%2==0 else 470;card(x,y,255,200,f'Ứng dụng {i+1}',BLUE if i%2==0 else TEAL)
            if i<4:
                ny=470 if i%2==0 else 270
                path(f'M{x+255},{y+100} C{x+277},{y+100} {x+267},{ny+100} {x+290},{ny+100}',TEAL,sw=3)
    elif p=='decision':
        card(100,380,350,160,'Kiểm tra',BLUE);line(467,465,540,465,arrow=True)
        poly('560,465 740,300 920,465 740,630');text(740,455,'Đủ điều kiện?',29,BLUE,'middle',700)
        path('M920,465 H1000 V330 H1090',arrow=True);path('M920,465 H1000 V610 H1090',arrow=True)
        text(1015,316,'Có',25,TEAL);text(1015,655,'Không',25,ORANGE)
        card(1110,255,375,150,'Thực hiện',TEAL);card(1110,540,375,150,'Bổ sung',ORANGE)
    elif p=='timeline':
        line(160,480,1450,480,arrow=True)
        for i in range(4):
            x=270+i*340;circle(x,480,16,BLUE,BLUE);yy=265 if i%2==0 else 555
            line(x,480,x,yy+125 if yy<480 else yy,BLUE,sw=3);card(x-140,yy,280,125,f'Mốc {i+1}',TEAL)
    elif p=='swimlane':
        for i,lab in enumerate(['Người dùng','Tác nhân','Hệ thống']):
            y=250+i*150;rect(100,y,1400,135,'white',BORDER,5);text(123,y+75,lab,26,TEAL,weight=700)
        card(370,275,270,85,'Giao việc');card(750,425,290,85,'Xử lý');card(1170,275,285,85,'Phê duyệt',TEAL);card(1160,575,300,85,'Lưu kết quả',TEAL)
        path('M650,320 H690 V468 H737',arrow=True);path('M1050,468 H1110 V320 H1155',arrow=True);path('M1320,370 V562',arrow=True)
    elif p=='funnel':
        for i,lab in enumerate(['Tập ban đầu','Qua sàng lọc','Đạt điều kiện']):
            top=1080-i*220;bottom=top-170;y=245+i*150
            poly(f'{800-top/2},{y} {800+top/2},{y} {800+bottom/2},{y+125} {800-bottom/2},{y+125}',fill=['#EFF6FF','#DBEAFE','#BFDBFE'][i]);text(800,y+72,lab,30,BLUE,'middle',700)
        text(800,750,'Minh họa cấu trúc — chưa gắn số liệu',22,GRAY,'middle')
    elif p=='pyramid':
        for pts,lab,x,y in [('800,230 590,410 1010,410','Định hướng',800,375),('565,440 1035,440 1180,570 420,570','Năng lực',800,525),('390,600 1210,600 1350,725 250,725','Nền tảng',800,680)]:poly(pts);text(x,y,lab,30,BLUE,'middle',700)
    elif p=='rings':
        for rad,col in [(245,'#EFF6FF'),(167,'#DBEAFE'),(83,'#BFDBFE')]:circle(760,478,rad,col,BLUE,2)
        text(760,490,'Lõi',31,BLUE,'middle',700);text(760,352,'Lớp gần',26,BLUE,'middle');text(760,268,'Phạm vi ngoài',25,BLUE,'middle');line(1010,475,1170,475,TEAL);text(1190,484,'Chú giải',28,TEAL)
    elif p=='venn':
        parts.append('<g opacity="0.55">');circle(650,470,215,'#DBEAFE',BLUE);circle(940,470,215,'#CCFBF1',TEAL);parts.append('</g>')
        text(555,470,'Tập A',33,BLUE,'middle',700);text(1030,470,'Tập B',33,TEAL,'middle',700);text(795,468,'Phần',24,NAVY,'middle');text(795,505,'giao',24,NAVY,'middle')
    elif p=='network':
        coords=[(300,335),(750,280),(1250,360),(440,630),(905,630),(1280,650)]
        for a,b in [(0,1),(1,2),(0,3),(1,3),(1,4),(2,4),(2,5),(3,4),(4,5)]:line(*coords[a],*coords[b],TEAL,sw=3)
        for i,(x,y) in enumerate(coords):circle(x,y,68,'white',BLUE);text(x,y+10,chr(65+i),32,BLUE,'middle',700)
    elif p=='dashboard':
        for i in range(3):card(115+i*470,235,440,130,f'Chỉ số {i+1}',BLUE)
        rect(115,400,865,320,'white',BLUE);rect(1020,400,480,320,'white',TEAL)
        for i,h in enumerate([100,160,125,210,180]):rect(170+i*150,675-h,95,h,BLUE,'none',5)
        circle(1260,553,95,'none',TEAL,34);text(1260,563,'Cơ cấu',23,TEAL,'middle');text(135,753,'Dữ liệu minh họa',21,GRAY)
    elif p=='chart':
        rect(110,235,960,465,'white',BORDER);line(190,640,1000,640,GRAY,sw=2);line(190,640,190,285,GRAY,sw=2)
        path('M220,580 L375,515 L530,550 L685,415 L840,440 L990,320',BLUE,sw=7)
        for x,y in [(220,580),(375,515),(530,550),(685,415),(840,440),(990,320)]:circle(x,y,7,BLUE,BLUE)
        card(1120,335,380,250,'Điểm cần chú ý',TEAL);text(130,745,'Dữ liệu minh họa — đơn vị và nguồn cần điền',21,GRAY)
    elif p=='executive':
        rect(115,235,1370,125,PALE,BLUE);text(800,307,'Kết luận cần quyết định',36,BLUE,'middle',700)
        for i in range(3):card(115+i*470,405,440,195,f'Bằng chứng {i+1}',TEAL)
        rect(115,650,1370,80,'#FFF7ED',ORANGE);text(800,701,'Hành động và phạm vi đề xuất',30,'#9A3412','middle',700)
    elif p=='bridge':
        card(110,280,510,380,'Hiện tại',GRAY);card(975,280,510,380,'Đề xuất',TEAL)
        line(650,460,940,460,arrow=True,sw=10);text(795,410,'Cơ chế thay đổi',24,BLUE,'middle');text(800,715,'Điều kiện để chuyển đổi',28,TEAL,'middle')
    elif p=='stat':
        rect(220,265,1160,430,PALE,BLUE);text(800,470,'THÔNG ĐIỆP NỔI BẬT',49,BLUE,'middle',800)
        text(800,555,'Một số liệu hoặc trích dẫn đã có nguồn',29,GRAY,'middle');text(800,633,'Phạm vi • thời gian • căn cứ',23,TEAL,'middle')
    elif p=='gantt':
        x0=410;yy=310
        for k in range(4):text(x0+k*260+120,275,f'Kỳ {k+1}',25,TEAL,'middle');line(x0+k*260,295,x0+k*260,715,BORDER,sw=2)
        for i,(start,duration) in enumerate([(0,1.3),(.9,1.8),(2.1,1.2),(3.1,.8)]):
            y=340+i*90;text(120,y+32,f'Hạng mục {i+1}',25,GRAY);rect(x0+start*260,y,duration*260,49,BLUE if i%2==0 else TEAL,'none',9)
    elif p=='sankey':
        path('M270,330 C570,330 585,455 795,455 S1130,360 1340,360',BLUE,sw=45)
        path('M270,640 C575,640 565,500 795,500 S1110,650 1340,650',TEAL,sw=45)
        for x,y,lab in [(115,250,'Nguồn A'),(115,580,'Nguồn B'),(1280,270,'Đích X'),(1280,590,'Đích Y')]:card(x,y,240,125,lab,BLUE if 'A' in lab or 'X' in lab else TEAL)
        text(800,754,'Luồng khái niệm — bề rộng chưa theo dữ liệu',23,GRAY,'middle')
    elif p=='fishbone':
        line(210,480,1240,480,arrow=True,sw=6)
        for x,y,lab in [(380,260,'Nhóm A'),(820,260,'Nhóm B'),(380,660,'Nhóm C'),(820,660,'Nhóm D')]:
            line(x,y+30 if y<480 else y-30,x+170,480,TEAL,sw=4);rect(x-70,y-44,250,95,'white',TEAL,12);text(x+55,y+13,lab,29,TEAL,'middle',700)
        card(1275,400,250,155,'Vấn đề',BLUE);text(800,759,'Giả thuyết nguyên nhân cần kiểm chứng',24,GRAY,'middle')
    else:raise ValueError('Unknown pattern '+p)
    line(90,802,1510,802,BORDER,sw=2)
    text(90,847,'Sơ đồ khung gốc • Không phải đối tượng SmartArt hoặc mẫu PPTX dựng sẵn',21,GRAY)
    text(1510,847,r['id'],22,BLUE,'end',700)
    parts.append('</svg>');return '\n'.join(parts)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('root',nargs='?',default=str(Path(__file__).resolve().parents[1]));args=parser.parse_args()
    root=Path(args.root).resolve();registry=json.loads((root/'archetypes/registry.json').read_text(encoding='utf-8'))
    if (root/'infographics/registry.json').exists():
        import subprocess, sys
        subprocess.run([sys.executable, str(root/'scripts/render_classified.py'), str(root)], check=True)
        return
    try:
        import cairosvg
        from PIL import Image,ImageDraw,ImageFont
    except ImportError as exc:raise SystemExit('Cần CairoSVG và Pillow để dựng lại PNG. Bản PNG đã có sẵn trong gói.') from exc
    out=root/'previews/layouts';out.mkdir(parents=True,exist_ok=True)
    for r in registry:
        svg=draw_layout(r);(out/(r['id']+'.svg')).write_text(svg,encoding='utf-8')
        cairosvg.svg2png(bytestring=svg.encode(),write_to=str(out/(r['id']+'.png')))
    font_candidates=[os.environ.get('AIA_FONT',''),'/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf','C:/Windows/Fonts/arial.ttf']
    fp=next((p for p in font_candidates if p and Path(p).exists()),None)
    if not fp:raise SystemExit('Cần đặt AIA_FONT tới font hỗ trợ tiếng Việt để dựng trang tổng hợp; không phân phối font cùng gói.')
    bold=fp.replace('Regular','Bold')
    if not Path(bold).exists():bold=fp
    ftitle=ImageFont.truetype(bold,64);fsub=ImageFont.truetype(fp,32);fcap=ImageFont.truetype(bold,27);fsmall=ImageFont.truetype(fp,27)
    for page in range(3):
        image=Image.new('RGB',(3200,1800),'#F8FAFC');d=ImageDraw.Draw(image)
        d.text((100,62),f'36 BỐ CỤC SLIDE — BẢNG {page+1}/3',font=ftitle,fill=NAVY)
        d.text((102,157),'Bản xem cấu trúc 16:9 • Chọn mã L để giao việc • Mỗi trang có tệp PNG và SVG riêng',font=fsub,fill=GRAY)
        for n,r in enumerate(registry[page*12:(page+1)*12]):
            col=n%4;row=n//4;x=100+755*col;y=246+490*row
            im=Image.open(out/(r['id']+'.png')).convert('RGB').resize((704,396),Image.Resampling.LANCZOS)
            image.paste(im,(x,y));d.rectangle((x,y,x+704,y+396),outline='#CBD5E1',width=2)
            caption=r['id']+' · '+r['name'];words=caption.split();lines=[];cur=''
            for word in words:
                cand=(cur+' '+word).strip()
                if d.textlength(cand,font=fcap)>704:lines.append(cur);cur=word
                else:cur=cand
            if cur:lines.append(cur)
            for k,l in enumerate(lines[:2]):d.text((x,y+410+k*35),l,font=fcap,fill=NAVY)
        d.text((100,1740),'Bản vẽ minh họa do gói dựng mới; không sao chép template thương mại.',font=fsmall,fill=GRAY)
        image.save(root/'previews'/f'contact-sheet-{page+1}.png')
    cards=[]
    for r in registry:
        cards.append(f'<article data-search="{html.escape(r["id"]+" "+r["name"]+" "+r["family"])}"><a href="layouts/{r["id"]}.png"><img loading="lazy" src="layouts/{r["id"]}.png" alt="{html.escape(r["name"])}" width="1600" height="900"></a><h2>{html.escape(r["id"]+" · "+r["name"])}</h2><p>{html.escape(r["purpose"])}</p><a href="../archetypes/{r["file"]}">Đọc đặc tả Markdown</a> · <a href="layouts/{r["id"]}.svg">Mở SVG</a></article>')
    page='''<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>36 bố cục slide AIA</title><style>*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;background:#f8fafc;color:#0a192f}header{padding:36px 5%;background:white;border-bottom:1px solid #cbd5e1}h1{font-size:32px;margin:0 0 12px}header p{max-width:1100px;line-height:1.6}input{width:min(650px,100%);font-size:18px;padding:14px;border:1px solid #64748b;border-radius:8px}main{padding:30px 5%;display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:25px}article{padding:14px;background:white;border:1px solid #cbd5e1;border-radius:14px}img{width:100%;height:auto;display:block;border-radius:8px}h2{font-size:19px;margin:15px 0 8px}p{line-height:1.6;color:#475569}a{color:#1e40af}article[hidden]{display:none}footer{padding:25px 5%}button{padding:10px}</style><header><h1>Thư viện 36 bố cục slide AIA</h1><p>Thư viện hoạt động ngoại tuyến sau khi giải nén. Nhấn hình để xem PNG đầy đủ; xem đặc tả Markdown để lấy mục tiêu, trường hợp sử dụng và prompt. Đây là sơ đồ khung do gói dựng mới, không phải 36 trang PowerPoint hoặc SmartArt gốc.</p><label for="q">Tìm mã, tên bố cục hoặc nhóm: </label><br><input id="q" type="search" placeholder="Ví dụ: L12, vòng lặp, dữ liệu" autocomplete="off"><p><a href="contact-sheet-1.png">Bảng 1</a> · <a href="contact-sheet-2.png">Bảng 2</a> · <a href="contact-sheet-3.png">Bảng 3</a> · <a href="../README.md">Hướng dẫn</a></p></header><main>'''+''.join(cards)+'''</main><footer>Không có tài nguyên tải ngoài, phông đính kèm, theo dõi hoặc kết nối mạng.</footer><script>const q=document.querySelector('#q');function norm(s){return s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').replace(/[đĐ]/g,'d').toLowerCase()}q.addEventListener('input',()=>{const t=norm(q.value);document.querySelectorAll('article').forEach(x=>{x.hidden=!norm(x.dataset.search).includes(t)})})</script></html>'''
    (root/'previews/index.html').write_text(page,encoding='utf-8')
    print(f'Rendered {len(registry)} SVG + PNG layouts, 3 contact sheets and offline HTML gallery.')
if __name__=='__main__':main()
