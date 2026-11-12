"""Build the concise Blender-illustrated assembly manual."""
from pathlib import Path
import json, math
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
ROOT=Path(__file__).resolve().parents[1];ASSETS=ROOT/'manual/assets/blender';OUT=ROOT/'pentos-assembly-manual.pdf'
for n,f in [('Regular','OpenSans-Regular.ttf'),('Bold','OpenSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(n,'/usr/share/fonts/open-sans/'+f))
pdfmetrics.registerFontFamily('Regular',normal='Regular',bold='Bold',italic='Regular',boldItalic='Bold')
W,H=612,792;M=42;INK='#20252b';BLUE='#1565c0';ORANGE='#e87500';GRAY='#59616b'
c=canvas.Canvas(str(OUT),pagesize=(W,H));c.setTitle('Pentos assembly');c.setAuthor('Pentos')
projections=json.loads((ASSETS/'projections.json').read_text())
guides=json.loads((ASSETS/'assembly-guides.json').read_text())
def text(x,y,t,size=10,color=INK,font='Regular'):
 c.setFont(font,size);c.setFillColor(HexColor(color));c.drawString(x,y,t)
def para(x,y,t,w=498,size=11):
 p=Paragraph(t,ParagraphStyle('p',fontName='Regular',fontSize=size,leading=16,textColor=HexColor(INK)));_,h=p.wrap(w,500);p.drawOn(c,x,y-h);return y-h

def diagram(img,labels,rect=(M,325,528,330)):
 im=Image.open(ASSETS/(img+'.png')).convert('RGBA');ow,oh=im.size
 bounds=im.getchannel('A').getbbox() or (0,0,ow,oh)
 left,top,right,bottom=bounds;pad=22;left=max(0,left-pad);top=max(0,top-pad);right=min(ow,right+pad);bottom=min(oh,bottom+pad)
 im=im.crop((left,top,right,bottom));w,h=im.size
 rx,ry,rw,rh=rect;scale=min(rw/w,rh/h);iw,ih=w*scale,h*scale;x=rx+(rw-iw)/2;y=ry+(rh-ih)/2
 def point(p):return x+(p[0]*ow-left)*scale,y+(p[1]*oh-(oh-bottom))*scale
 c.drawImage(ImageReader(im),x,y,iw,ih,mask='auto')
 # Dotted insertion axes are separate from the solid part labels.
 c.saveState();c.setStrokeColor(HexColor('#63778c'));c.setLineWidth(.85);c.setLineCap(1);c.setDash(1,3)
 for start,end in ([] if img.startswith('08-') else guides.get(img,[])):
  sx,sy=point(start);ex,ey=point(end)
  c.line(sx,sy,ex,ey)
  angle=math.atan2(ey-sy,ex-sx);length=4
  c.saveState();c.setDash();c.line(ex,ey,ex-length*math.cos(angle-.5),ey-length*math.sin(angle-.5));c.line(ex,ey,ex-length*math.cos(angle+.5),ey-length*math.sin(angle+.5));c.restoreState()
 c.restoreState()
 for j,(idx,label,side) in enumerate(labels):
  tx,ty=point(projections[img][str(idx)])
  lx=rx+6 if side=='left' else rx+rw-132;ly=ry+rh+14 if j==0 else ry-14
  color=ORANGE if idx in (14,5,37) else BLUE
  c.setLineWidth(.75);c.setStrokeColor(HexColor(color));c.line(lx+50,ly-4 if j==0 else ly+11,tx,ty);c.setFillColor(HexColor(color));c.circle(tx,ty,2.1,fill=1,stroke=0)
  text(lx,ly,label,9,color,'Bold')

def page(num,title,img,labels,instructions,note=None):
 c.setFillColor(white);c.rect(0,0,W,H,fill=1,stroke=0)
 text(M,707,f'{num:02}',26,BLUE,'Bold');text(M+48,707,title,24,INK,'Bold')
 if img=='cradle-hardware-details':
  text(M,682,'Motor and assembled bearing',10,ORANGE,'Bold');text(M+276,682,'Screws from underneath',10,BLUE,'Bold')
  diagram('04b-cradle-hardware',[(13,'B motor','left'),(22,'Assembled thrust bearing','right')],(M,345,252,310))
  diagram('04c-motor-screws',[(70,'4 x M3 motor screws','left'),(14,'Cradle underside','right')],(M+276,345,252,310))
 elif img=='drive-details':
  text(M,682,'Belt and pulleys',10,BLUE,'Bold');text(M+276,682,'Underside screw',10,BLUE,'Bold')
  diagram('06-b-drive',[(12,'20T driven pulley','left')],(M,345,252,310))
  diagram('06c-screw-detail',[(12,'Driven pulley','left'),(40,'M4 x 16 mm screw','right')],(M+276,345,252,310))
 elif img=='hub-details':
  text(M,682,'Drive side',10,ORANGE,'Bold');text(M+276,682,'Opposite side',10,ORANGE,'Bold')
  diagram('07-hub-left',[(5,'Sonic Hub','left'),(2,'REX shaft','right')],(M,345,252,310))
  diagram('07-hub-right',[(37,'Sonic Hub','left'),(6,'REX shaft','right')],(M+276,345,252,310))
 elif img=='gantry-mount-details':
  text(M,682,'Mounted mechanism',10,BLUE,'Bold');text(366,682,'Mounting detail',10,BLUE,'Bold')
  diagram('09-mounted',[(100,'Y gantry','left'),(106,'Original leveling knobs','right')],(M,345,300,310))
  diagram('09-mount-detail',[(110,'Original M4 bed screw','left'),(15,'Holder foot','right')],(366,345,204,310))
 elif img=='homing-details':
  text(M,682,'A / tilt',10,ORANGE,'Bold');text(M+276,682,'B / rotation',10,BLUE,'Bold')
  diagram('08-a-homing',[(10,'Hall sensor','left'),(36,'Embedded magnet','right')],(M,345,252,310))
  diagram('08-b-homing',[(18,'Hall sensor','left'),(26,'Embedded magnet','right')],(M+276,345,252,310))
 else:diagram(img,labels)
 c.setStrokeColor(HexColor('#cfd3d8'));c.setLineWidth(.6);c.line(M,300,W-M,300)
 yy=275
 for i,t in enumerate(instructions,1):
  text(M,yy-11,str(i)+'.',11,BLUE,'Bold');yy=para(M+24,yy,t,w=504,size=11)-17
 if note:
  para(M,102,note,w=528,size=9)
 c.showPage()

def title_page():
 c.setFillColor(white);c.rect(0,0,W,H,fill=1,stroke=0)
 text(M,708,'PENTOS',48,BLUE,'Bold')
 text(M,674,'Assembly manual',22,INK)
 im=Image.open(ROOT/'manual/assets/pentos-paper-render.png').convert('RGBA')
 bounds=im.getchannel('A').getbbox()
 if bounds:
  l,t,r,b=bounds;im=im.crop((max(0,l-12),max(0,t-12),min(im.width,r+12),min(im.height,b+12)))
 iw,ih=im.size;scale=min(528/iw,565/ih);w,h=iw*scale,ih*scale
 c.drawImage(ImageReader(im),M+(528-w)/2,60+(565-h)/2,w,h,mask='auto')
 c.showPage()

title_page()
from magnet_pages import build as build_magnet_pages
build_magnet_pages(c,text,para)
page(1,'Assemble the bed','01-bed',[(80,'4 x M3 x 35 mm screws','left'),(30,'32 mm REX shaft','right')],[
 'Fit four 15 mm standoffs, silicone spacers and the heatbed to the B base.',
 'Insert four M3 x 35 mm screws from underneath. Tighten evenly.',
 'Add the print surface. Insert the 32 mm REX shaft from the bed side; set the bed aside.'
])
page(2,'Fit the Sonic Hubs','02-hubs',[(50,'4 x M4 x 12 mm per side','left'),(5,'Sonic Hub (inside)','right')],[
 'Fit both Sonic Hubs inside the cradle.',
 'Attach each hub with four M4 x 12 mm screws from inside. Leave the shaft clamps loose.'
])
page(3,'Prepare the holders','03-holders',[(1,'52 mm shaft / fitted E-clip','left'),(11,'Back holder / 32 mm shaft','right')],[
 'Seat the flanged bearings in both holders.',
 'Leave both factory E-clips attached. Slide the 40T pulley onto the 52 mm shaft’s free end.',
 'Insert each shaft from its clipped side. The clips stay outside the holders.'
])
page(4,'Fit the A-axis drive','04-a-drive',[(60,'4 x M3 motor screws','left'),(38,'A motor (inside)','right')],[
 'Mount the A motor inside the front holder with four M3 screws from outside.',
 'Fit the 20T pulley and belt. Align both pulleys and tighten their grub screws.'
], 'Belts: GT2, 6 mm wide, 184 mm pitch length (92 teeth).')
page(5,'Fit the cradle bearing','04a-cradle-bearing',[(7,'Assembled flanged bearing','left'),(14,'Round bearing seat','right')],[
 'Insert the assembled flanged bearing from underneath the cradle.',
 'Seat the flange flat and square against the cradle.'
])
page(6,'Motor and thrust bearing','cradle-hardware-details',[],[
 'Seat the assembled thrust bearing on the cradle. Keep its stack together.',
 'Place the B motor on top. Fasten with four M3 screws from underneath.'
])
page(7,'Fit cradle between holders','04d-fit-cradle',[(15,'Drive-side holder','left'),(37,'Sonic Hub','right')],[
 'Fit the prepared holders to the cradle, sliding their shafts into the Sonic Hubs.',
 'Leave the hub clamps loose. Check that the cradle tilts freely.'
])
page(8,'Fit the bed to the cradle','05-bed-on-cradle',[(27,'B-axis base','left'),(14,'A-axis cradle','right')],[
 'Check that both cradle bearings are seated.',
 'Lower the bed and guide its shaft through the bearing stack.'
])
page(9,'Install the B drive','06c-screw-detail',[(12,'20T driven pulley','left'),(40,'M4 x 16 mm screw','right')],[
 'Fit both 20T pulleys and the B belt under the cradle.',
 'Insert the M4 x 16 mm screw from underneath to secure the pulley and bed.',
 'Align the pulleys, tighten the grub screws and check that the bed rotates freely.'
])
page(10,'Align and tighten','hub-details',[],[
 'Center the cradle and square the shafts.',
 'Fit any remaining hub screws. Tighten both hub clamps and all mounting screws.',
 'Move A and B by hand; check for binding and belt misalignment.'
])
page(11,'Mount the Hall sensors','homing-details',[],[
 'Secure the Hall sensors beside the embedded magnets with hot glue.',
 'Route wires clear of the belts, with slack for both axes.',
 'Check both sensor signals before homing. Limit B travel to prevent cable twisting.'
])
page(12,'Mount on the Y gantry','gantry-mount-details',[],[
 'Seat the four holder feet directly on the Y gantry.',
 'Insert the original M4 countersunk bed screws from above, through the feet and gantry.',
 'Refit the leveling knobs underneath and tighten evenly. Check that the full Y travel is clear.'
])
c.save();print(OUT)
