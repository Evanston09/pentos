"""Part-specific print preparation pages using Blender and actual Prusa toolpaths."""
from pathlib import Path
import json, math
from PIL import Image
from reportlab.lib.colors import HexColor,white
from reportlab.lib.utils import ImageReader
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'manual/assets/magnet-preparation'
META=json.loads((ROOT/'manual/slicing/magnet-pause-results.json').read_text())
PROJ=json.loads((ASSETS/'render-projections.json').read_text())
BLUE='#1565c0';ORANGE='#e87500';RED='#ae3026';GRAY='#59616b';INK='#20252b';M=42

def build(c,text,para):
 def header(code,title):
  c.setFillColor(white);c.rect(0,0,612,792,fill=1,stroke=0)
  text(M,707,code,24,BLUE,'Bold');text(110,707,title,24,INK,'Bold')
 def footer():
  c.showPage()
 def image(name,rect,point=None):
  im=Image.open(ASSETS/(name+'.png')).convert('RGBA');ow,oh=im.size
  # Full views retain build-plate context; detail views crop around the pocket.
  if name.endswith('-detail'):
   bounds=(330,235,1150,845) if name.startswith('a-') else (380,445,1130,855)
  else:bounds=(0,0,ow,oh)
  l,t,r,b=bounds;im=im.crop(bounds);iw,ih=im.size
  rx,ry,rw,rh=rect;sc=min(rw/iw,rh/ih);x=rx+(rw-iw*sc)/2;y=ry+(rh-ih*sc)/2
  c.drawImage(ImageReader(im),x,y,iw*sc,ih*sc,mask='auto')
  def pt(key):
   u,v=PROJ[name][key];return x+(u*ow-l)*sc,y+(v*oh-(oh-b))*sc
  if point:
   px,py=pt(point);c.saveState();c.setStrokeColor(HexColor(RED));c.setLineWidth(1.2);c.setDash(2,2);c.circle(px,py,10 if name.startswith('a-') else 17,stroke=1,fill=0);c.restoreState()
  return pt
 def line_label(point,label,x,y,color=RED):
  px,py=point;c.setStrokeColor(HexColor(color));c.setFillColor(HexColor(color));c.setLineWidth(.8);c.line(x+35,y-5,px,py);c.circle(px,py,2,fill=1,stroke=0);text(x,y,label,9,color,'Bold')
 def strip(y,title,subtitle):
  c.setFillColor(HexColor('#fff1eb'));c.rect(M,y,528,56,fill=1,stroke=0)
  c.setFillColor(HexColor(RED));c.rect(M,y,4,56,fill=1,stroke=0)
  text(M+14,y+35,title,12,RED,'Bold');text(M+14,y+15,subtitle,9,INK)
 def numbered(y,items,size=10.5):
  for i,t in enumerate(items,1):
   text(M,y-size,f'{i}.',size,BLUE,'Bold');y=para(M+23,y,t,w=505,size=size)-13
  return y
 def toolpaths(name,layer,rect):
  rec=META[name];segments=json.loads((ASSETS/f'{name}-toolpaths.json').read_text())[str(layer)]
  rx,ry,rw,rh=rect;cx,cy=rec['gcode_center'];is_a=name.startswith('a-')
  # Rotate cradle's top view 90 degrees to show its narrow rectangular pocket clearly.
  radiusx,radiusy=(10,5.5) if is_a else (9.5,7.5)
  sc=min(rw/(2*radiusx),rh/(2*radiusy));ox=rx+rw/2;oy=ry+rh/2
  def point(x,y):
   dx,dy=x-cx,y-cy
   if is_a:dx,dy=dy,-dx
   return ox+dx*sc,oy+dy*sc
  c.saveState();path=c.beginPath();path.rect(rx,ry,rw,rh);c.clipPath(path,stroke=0,fill=0)
  c.setFillColor(HexColor('#f7f8fa'));c.rect(rx,ry,rw,rh,fill=1,stroke=0)
  for x,y,nx,ny,role,z in segments:
   if max(abs(x-cx),abs(nx-cx))>25 and max(abs(y-cy),abs(ny-cy))>25:continue
   color=ORANGE if role=='Bridge infill' else BLUE if 'perimeter' in role.lower() else '#adb5be'
   c.setStrokeColor(HexColor(color));c.setLineWidth(.45*sc*.88);c.setLineCap(1);c.line(*point(x,y),*point(nx,ny))
  # Dashed red line identifies the magnet footprint, not an extruded toolpath.
  c.setLineWidth(.85);c.setDash(2,2);c.setStrokeColor(HexColor(RED))
  if is_a:c.rect(ox-6*sc,oy-1.5*sc,12*sc,3*sc,stroke=1,fill=0)
  else:c.circle(ox,oy,6*sc,stroke=1,fill=0)
  c.restoreState()

 header('00','Embed the magnets')
 strip(625,'CHECK MAGNET POLARITY','Test with the Hall sensor. The wrong face will be sealed inside.')
 for x,name,label in [(M,'a-axis-cradle','A / cradle'),(318,'b-axis-base','B / bed base')]:
  text(x,595,label,13,ORANGE if name.startswith('a-') else BLUE,'Bold')
  image(name+'-full',(x,375,252,205),'pocket')
 text(M,323,'Dashed circle = magnet pocket',9,RED,'Bold')
 numbered(294,[
  '<b>Test each 12 x 3 mm disc magnet with its Hall sensor in the installed orientation.</b> Confirm the homing input triggers near the magnet and releases when removed. Flip the magnet if needed.',
  '<b>Mark the working face TO SENSOR.</b> Point it toward the cradle’s outer end wall (A), or down toward the print bed (B).',
  '<b>Recheck polarity at the print pause.</b> Seat the magnet below the next toolpath before resuming.'
 ],11)
 footer()

 for name,code,title in [('a-axis-cradle','00A','Print the A cradle'),('b-axis-base','00B','Print the B base')]:
  rec=META[name];a=name.startswith('a-');header(code,title)
  c.setFillColor(HexColor('#edf4fc'));c.rect(M,626,528,58,fill=1,stroke=0)
  text(M+12,660,f'PAUSE BEFORE Z {rec["pause_z"]:.2f} mm',17,BLUE,'Bold')
  text(M+12,640,f'Object layer {rec["object_layer"]}  /  Preview layer {rec["preview_layer"]}'+(' (includes supports)' if a else ''),10,BLUE,'Bold')
  image(name+'-full',(M,421,252,177),'pocket')
  p=image(name+'-detail',(318,421,252,177))
  line_label(p('mark'),'TO SENSOR',335,584)
  text(318,410,'Face toward outer end wall' if a else 'Face DOWN toward the print bed',9,RED,'Bold')
  text(M,383,f'LAST OPEN: Z {rec["last_open_z"]:.2f} mm',10,BLUE,'Bold')
  text(318,383,f'FIRST COVER: Z {rec["pause_z"]:.2f} mm',10,ORANGE,'Bold')
  toolpaths(name,rec['last_open_preview_layer'],(M,240,252,132));toolpaths(name,rec['preview_layer'],(318,240,252,132))
  numbered(199,[
   'Select your printer and confirm its pause command. At the first-cover layer, add <b>Insert pause print</b>.',
   'At the pause, seat the magnet below the next toolpath. Resume to enclose it.'
  ],10)
  strip(63,'RECHECK POLARITY BEFORE RESUMING.', 'A: marked face toward outer end wall.' if a else 'B: marked face DOWN toward the print bed.')
  footer()
