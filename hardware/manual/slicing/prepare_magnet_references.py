"""Verify pocket closures against actual PrusaSlicer G-code and make pause projects."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import xml.etree.ElementTree as ET
import json,re,hashlib,subprocess
import numpy as np
ROOT=Path(__file__).resolve().parents[2];WORK=ROOT/'tmp/pdfs/magnet-slicing';OUT=ROOT/'manual/slicing';ASSETS=ROOT/'manual/assets/magnet-preparation'
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
cases={'a-axis-cradle':dict(config='a-axis-cradle-reference.ini',pause=14.4,base='a-axis-reference.3mf',sensor_face='+X / outer end of cradle'), 'b-axis-base':dict(config='magnet-layer-reference.ini',pause=4.2,base='b-axis-reference.3mf',sensor_face='-Z / toward print bed')}
manifest={}
for name,case in cases.items():
 source=ROOT/'printable-parts'/f'{name}.3mf'
 with ZipFile(source) as z:tree=ET.fromstring(z.read('3D/3dmodel.model'))
 vertices=np.array([[float(a.get(k))*1000 for k in ('x','y','z')] for a in tree.findall('.//m:vertex',NS)])
 faces=np.array([[int(a.get(k)) for k in ('v1','v2','v3')] for a in tree.findall('.//m:triangle',NS)])
 parent=np.arange(len(vertices))
 def find(a):
  while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
  return a
 for tri in faces:
  r=find(tri[0])
  for p in tri[1:]:parent[find(p)]=r
 groups={}
 for j in range(len(vertices)):groups.setdefault(find(j),[]).append(j)
 cavity=vertices[min(groups.values(),key=len)]
 # Rotate +90 degrees around X: the native Y-up model becomes Z-up.
 v=np.column_stack((vertices[:,0],-vertices[:,2],vertices[:,1]));cv=np.column_stack((cavity[:,0],-cavity[:,2],cavity[:,1]))
 shift=np.array([110,110])-(v[:,:2].min(0)+v[:,:2].max(0))/2
 pocket=(cv.min(0)+cv.max(0))/2;floor=float(cv[:,2].min());roof=float(cv[:,2].max());center=pocket[:2]+shift
 hx=min(float(np.ptp(cv[:,0]))/2-.5,3);hy=min(float(np.ptp(cv[:,1]))/2-.5,5.5)
 paths={};heights={};hits={};x=y=e=0.;layer=0;z=0;role=''
 def intersects(x,y,nx,ny):
  # Liang-Barsky line/rectangle intersection, inset from cavity perimeter.
  lo=0.;hi=1.
  for p,q in [(-(nx-x),x-(center[0]-hx)),(nx-x,center[0]+hx-x),(-(ny-y),y-(center[1]-hy)),(ny-y,center[1]+hy-y)]:
   if abs(p)<1e-12:
    if q<0:return False
   elif p<0:lo=max(lo,q/p)
   else:hi=min(hi,q/p)
   if lo>hi:return False
  return True
 gcode=(WORK/f'{name}.gcode').read_text()
 for line in gcode.splitlines():
  if line.startswith(';LAYER_CHANGE'):layer+=1;paths[layer]=[]
  if line.startswith(';Z:'):z=float(line[3:]);heights[layer]=z
  if line.startswith(';TYPE:'):role=line[6:]
  code=line.split(';')[0].strip()
  if code.startswith('G92'):
   m=re.search(r'E([-+\d.]+)',code)
   if m:e=float(m[1])
  if not code.startswith(('G1 ','G0 ')):continue
  args={k:float(value) for k,value in re.findall(r'([XYE])([-+\d.]+)',code)}
  nx,ny,ne=args.get('X',x),args.get('Y',y),args.get('E',e)
  if ne>e+1e-6 and (nx!=x or ny!=y):
   paths.setdefault(layer,[]).append([x,y,nx,ny,role,z])
   if intersects(x,y,nx,ny):hits.setdefault(layer,[]).append(role)
  x,y,e=nx,ny,ne
 cap=min(k for k in hits if heights[k]>=roof-.05)
 assert abs(heights[cap]-case['pause'])<1e-6,(name,cap,heights[cap])
 assert 'Bridge infill' in hits[cap],(name,hits[cap])
 last=max(k for k,lines in paths.items() if heights[k]<heights[cap] and any('Support' not in s[4] for s in lines))
 assert last not in hits,(name,'last open layer is not open')
 assert not any(floor+.4<heights[k]<roof-.2 for k in hits),'Pocket contains extruded material or support'
 record=dict(pause_z=heights[cap],preview_layer=cap,object_layer=round(heights[cap]/.2),last_open_z=heights[last],last_open_preview_layer=last,last_open_object_layer=round(heights[last]/.2),pocket_min=cv.min(0).tolist(),pocket_max=cv.max(0).tolist(),pocket_center=pocket.tolist(),print_size=np.ptp(v,axis=0).tolist(),gcode_center=center.tolist(),sensor_face=case['sensor_face'],source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),support='build-plate-only snug' if name.startswith('a-') else 'none',prusa_version='2.9.6')
 manifest[name]=record
 np.savez_compressed(ASSETS/f'{name}-print-mesh.npz',vertices=v,faces=faces)
 (ASSETS/f'{name}-toolpaths.json').write_text(json.dumps({str(last):paths[last],str(cap):paths[cap]}))
 # Native PrusaSlicer pause event: the selected printer preset supplies its command.
 events=ET.Element('custom_gcodes_per_print_z',bed_idx='0')
 ET.SubElement(events,'code',print_z=str(heights[cap]),type='1',extruder='1',color='',extra='STOP: Check magnet polarity, seat magnet below printed surface, then resume.',gcode='M601')
 ET.SubElement(events,'mode',value='SingleExtruder')
 profile=gcode[gcode.index('; prusaslicer_config = begin'):]
 profile=re.sub(r'^; print_settings_id =.*$', '; print_settings_id = Pentos magnet pause reference',profile,flags=re.M)
 profile=re.sub(r'^; printer_settings_id =.*$', '; printer_settings_id = REFERENCE - select your actual printer',profile,flags=re.M)
 target=OUT/f'{name}-magnet-pause.3mf'
 with ZipFile(WORK/case['base']) as srczip,ZipFile(target,'w',ZIP_DEFLATED) as dest:
  for item in srczip.infolist():dest.writestr(item,srczip.read(item.filename))
  dest.writestr('Metadata/Slic3r_PE.config',profile)
  dest.writestr('Metadata/Prusa_Slicer_custom_gcode_per_print_z.xml',ET.tostring(events,encoding='utf-8',xml_declaration=True))
 print(name,'pause before Preview',cap,'object layer',record['object_layer'],'Z',heights[cap],'last open',heights[last])
(OUT/'magnet-pause-results.json').write_text(json.dumps(manifest,indent=2))
