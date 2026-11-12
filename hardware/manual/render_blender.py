"""Blender assembly illustrations. Run: blender -b -t 6 -noaudio -P manual/render_blender.py"""
import bpy, math, json, sys
from pathlib import Path
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'manual/assets/blender';OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.render.threads_mode='FIXED';scene.render.threads=6

sys.path.insert(0,str(Path(__file__).parent))
from render_style import configure, materials
configure(scene)
style=materials()
blue,orange,metal,black,plate,heater,silicone,sensor,magnet,beltmat=[style[k] for k in ('blue','orange','metal','black','plate','heater','silicone','sensor','magnet','beltmat')]
# Measured axial limits of the 7 mm tooth bands in the supplied assembly.
a_tooth_bands={0:(-1.2298666808,-1.1598666808),9:(-1.2568666808,-1.1868666808)}
a_plane=sum(a_tooth_bands[9])/2
a_motor_shift=a_plane-sum(a_tooth_bands[0])/2
assert abs(a_motor_shift+.027)<1e-7
data=np.load(ROOT/'manual/assets/meshes.npz');objects={}
for i in range(len(data.files)//3):
 n=str(data[f'n{i}']);v=data[f'v{i}'];v=np.column_stack((v[:,0],-v[:,2],v[:,1]))*.01;f=data[f'f{i}']
 if i==0:v[:,0]+=a_motor_shift
 mesh=bpy.data.meshes.new(n);mesh.from_pydata(v.tolist(),[],f.tolist());mesh.update()
 ob=bpy.data.objects.new(n,mesh);ob['cad_index']=i;scene.collection.objects.link(ob);objects[i]=ob
 mat=orange if i==14 else blue if i in (11,15,27) else black if i in (13,38) else plate if i==24 else heater if i==34 else silicone if i in (25,32,33,35) else sensor if i in (10,18) else magnet if i in (26,36) else metal
 mesh.materials.append(mat)
 ob.color=(1,0,0,1) if i in (11,15) else (0,.630891264,.775871261,1)
 # Weld triangulated CAD surfaces before smoothing their normals.
 bpy.context.view_layer.objects.active=ob;ob.select_set(True)
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.remove_doubles(threshold=.000005);bpy.ops.object.mode_set(mode='OBJECT');ob.select_set(False)
 for poly in mesh.polygons:poly.use_smooth=True
 mesh.set_sharp_from_angle(angle=math.radians(35))
 # Preserve crisp CAD edges while smoothing curved surfaces.
 mod=ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL');mod.keep_sharp=True

# Socket screws are schematic; mount centers are measured from CAD hole loops.
Nbolt=Vector((0,.630891264,.775871261)).normalized()
def screw(idx,name,seat,axis,diameter,length):
 axis=Vector(axis).normalized();seat=Vector(seat);pieces=[];head_depth=diameter;head_radius=diameter*.875
 for radius,depth,center in [(diameter/2,length,seat+axis*length/2),(head_radius,head_depth,seat-axis*head_depth/2)]:
  bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius,depth=depth,location=center)
  ob=bpy.context.object;ob.rotation_euler=axis.to_track_quat('Z','Y').to_euler();ob.data.materials.append(metal);pieces.append(ob)
 bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=diameter*.44,depth=head_depth*.7,location=seat-axis*head_depth*.9)
 cut=bpy.context.object;cut.rotation_euler=axis.to_track_quat('Z','Y').to_euler();head=pieces[1];mod=head.modifiers.new('Hex socket','BOOLEAN');mod.object=cut;bpy.context.view_layer.objects.active=head;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in pieces:ob.select_set(True)
 bpy.context.view_layer.objects.active=head;bpy.ops.object.join();head.name=name;head['cad_index']=idx;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);objects[idx]=head
screw(40,'M4 x 16 mm underside screw',Vector((-.0519,-.37975,.36865))-Nbolt*.10,Nbolt,.04,.16)
anchors=json.loads((ROOT/'manual/assets/fastener-anchors.json').read_text())
def convert(p):return Vector((p[0],-p[2],p[1]))*.01
hub_left=set(range(50,54));hub_right=set(range(54,58));hub_screws=hub_left|hub_right
a_screws=set(range(60,64));b_screws=set(range(70,74))
for first,key,axis in [(50,'5',(1,0,0)),(54,'37',(-1,0,0))]:
 for k,p in enumerate(anchors[key][0]):screw(first+k,'M4 x 12 mm hub attachment',convert(p)+Vector(axis)*.08,-Vector(axis),.04,.12)
for first,key,axis in [(60,'A_motor',Vector((1,0,0))),(70,'B_motor',Nbolt)]:
 for k,p in enumerate(anchors[key]):screw(first+k,'M3 motor mounting screw',convert(p)-axis*.04,axis,.03,.08)

bed_screws=set(range(80,84))
for k,p in enumerate(anchors['34'][2]):
 seat=convert(p);seat-=Nbolt*(seat.dot(Nbolt)-.29644)
 screw(80+k,'M3 x 35 mm heatbed screw',seat,Nbolt,.03,.35)

camdata=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',camdata);scene.collection.objects.link(cam);scene.camera=cam;camdata.type='ORTHO';camdata.lens=50
# Smooth open-belt paths at the modeled pulley center planes; schematic tooth detail.
def make_belt(name,centers,radii,normal):
 c1,c2=map(Vector,centers);n=Vector(normal).normalized();u=(c2-c1).normalized();v=n.cross(u).normalized();a=math.acos((radii[0]-radii[1])/(c2-c1).length)
 pts=[]
 for center,r,start,end in [(c1,radii[0],a,2*math.pi-a),(c2,radii[1],-a,a)]:
  for t in np.linspace(start,end,60):pts.append(center+r*(math.cos(t)*u+math.sin(t)*v))
 verts=[]
 for p in pts:
  for off in (-.03,.03):verts.append(tuple(p+n*off))
 faces=[]
 for j in range(len(pts)):
  k=(j+1)%len(pts);faces.append((2*j,2*k,2*k+1,2*j+1))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.materials.append(beltmat)
 ob=bpy.data.objects.new(name,mesh);scene.collection.objects.link(ob);sol=ob.modifiers.new('Belt thickness','SOLIDIFY');sol.thickness=.012
 return ob
# Match the A motor pulley to the driven groove, then fit its true circular axes.
def a_axis_center(idx,ring_x,radius):
 coords=np.array([tuple(v.co) for v in objects[idx].data.vertices]);yz=coords[:,1:]
 rough=(yz.min(0)+yz.max(0))/2
 mask=(abs(coords[:,0]-ring_x)<1e-6)&(np.linalg.norm(yz-rough,axis=1)>radius-.0001)
 ring=yz[mask];assert len(ring)>=24
 fit=np.linalg.lstsq(np.column_stack((2*ring[:,0],2*ring[:,1],np.ones(len(ring)))),np.sum(ring*ring,axis=1),rcond=None)[0]
 assert np.max(abs(np.linalg.norm(ring-fit[:2],axis=1)-radius))<1e-6
 return (a_plane,float(fit[0]),float(fit[1]))
a_centers=[a_axis_center(0,-1.2308666808+a_motor_shift,.075),a_axis_center(9,-1.2593666808,.135)]
for idx,(lo,hi) in a_tooth_bands.items():
 shift=a_motor_shift if idx==0 else 0
 assert lo+shift <= a_plane-.03 and a_plane+.03 <= hi+shift
# The shifted motor pulley remains entirely on the original motor shaft.
assert min(v.co.x for v in objects[0].data.vertices)>min(v.co.x for v in objects[38].data.vertices)
a_belt=make_belt('A belt',a_centers,[20*.02/(2*math.pi),40*.02/(2*math.pi)],(1,0,0))
a_belt.modifiers['Belt thickness'].offset=.6
print('A BELT: shared groove plane',a_plane,'motor pulley shift',a_motor_shift,'centers',a_centers,flush=True)

# Both 6 mm belt edges must fit inside both CAD tooth bands.
# Values are axial limits of the toothed faces, in Blender units (100 mm/unit).
b_tooth_bands={12:(-.028555,.041445),19:(-.031555,.038445)}
b_half_width=.03
b_plane=sum(sum(band) for band in b_tooth_bands.values())/4
for lo,hi in b_tooth_bands.values():assert lo <= b_plane-b_half_width and b_plane+b_half_width <= hi

def b_axis_center(idx):
 # Fit the circular flange ring at the tooth-band boundary. The complete
 # part bounds include the asymmetric set-screw boss, so they bias the axis.
 u=Vector((1,0,0));v=Nbolt.cross(u).normalized()
 coords=np.array([tuple(vert.co) for vert in objects[idx].data.vertices])
 xy=coords@np.array([tuple(u),tuple(v)]).T
 rough=(xy.min(0)+xy.max(0))/2
 mask=(abs(coords@np.array(Nbolt)-b_tooth_bands[idx][0])<1e-5)&(np.linalg.norm(xy-rough,axis=1)>.07)
 ring=xy[mask];assert len(ring)>=12
 fit=np.linalg.lstsq(np.column_stack((2*ring[:,0],2*ring[:,1],np.ones(len(ring)))),np.sum(ring*ring,axis=1),rcond=None)[0]
 radius=np.sqrt(fit[2]+fit[0]**2+fit[1]**2)
 assert np.max(abs(np.linalg.norm(ring-fit[:2],axis=1)-radius))<1e-5
 return u*float(fit[0])+v*float(fit[1])+Nbolt*b_plane
b_centers=[b_axis_center(19),b_axis_center(12)]
assert abs((b_centers[1]-b_centers[0]).dot(Nbolt))<1e-6
b_belt=make_belt('B belt',b_centers,[.06366198,.06366198],Nbolt)
# Place the belt's inner face at the tooth tips and its body outward.
b_belt.modifiers['Belt thickness'].offset=.6
print('B BELT: shared groove plane',b_plane,'centers',[tuple(c) for c in b_centers],flush=True)
all_ids=set(objects)
bed={7,8,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35}|bed_screws
cradle={14,5,37}|hub_screws
holders={11,15,2,6,1,3,4,16,17}
axis_a={0,9,38}|a_screws
axis_b={12,13,19}|b_screws
N=Vector((0,.627,.779)).normalized()
def along(ids,amount):return {i:tuple(N*amount) for i in ids}
plate_ids={24,34};spacer_ids={25,32,33,35};standoff_ids={23,28,29,31}
bed_moving=bed-{7,8,20,21,22}
stages=[
 ('01-bed',bed-{7,8,20,21,22},(1,-1,1.65),{**along({24},1.05),**along({34},.85),**along(bed_screws,-.6),**along(spacer_ids,.48),**along(standoff_ids,.22),**along({30},.45)},False,False),
 ('02-hubs',cradle,(1,-1,.95),{5:(.4,0,0),37:(-.4,0,0),**{i:(.65,0,0) for i in hub_left},**{i:(-.65,0,0) for i in hub_right}},False,False),
 ('03-holders',holders|{9},(-.7,-1,.8),{2:(-.65,0,0),1:(-.65,0,0),3:(-.28,0,0),4:(-.28,0,0),6:(.65,0,0),16:(.28,0,0),17:(.28,0,0),9:(-.65,0,0)},False,False),
 ('04-a-drive',holders|axis_a,(-1,-1,.85),{38:(.5,0,0),**{i:(-.35,0,0) for i in a_screws}},True,False),
 ('04a-cradle-bearing',cradle|{7,8},(1,-1,-.6),along({7,8},-.35),False,False),
 ('04b-cradle-hardware',cradle|{13,7,8,20,21,22},(1,-1,1.6),{**along({13},.45),**along({20,21,22},.4)},False,False),
 ('04c-motor-screws',cradle|{13,7,8,20,21,22}|b_screws,(1,-1,-.5),along(b_screws,-.35),False,False),
 ('04d-fit-cradle',cradle|holders|axis_a|b_screws|{13,7,8,20,21,22},(1,-1,1.1),{**{i:(-.4,0,0) for i in ({15,2,1,3,4,9,38,0}|a_screws)},**{i:(.4,0,0) for i in {11,6,16,17}}},True,False),
 ('05-bed-on-cradle',bed|cradle|holders|axis_a|{13}|b_screws,(1,-1,1.6),along(bed_moving,.85),True,False),
 ('06-b-drive',bed|cradle|holders|axis_a|axis_b|{40},(.05,-1,-.45),{**along({19,12},-.3),**along({40},-.9)},True,True),
 ('06c-screw-detail',bed|cradle|b_screws|{12,40,13,19,7,8,20,21,22},(1,-1,-.6),along({40},-.5),False,True),
 ('07-tighten',all_ids,(-1,1,1.1),{},True,True),
 ('overview',all_ids,(1,1,1.25),{},True,True),
 ('07-hub-left',{14,5,2}|hub_left,(1,-1,.7),{},False,False),
 ('07-hub-right',{14,37,6}|hub_right,(-1,-1,.7),{},False,False),
 ('08-a-homing',{10,36,11,14},(-1,-1,.3),{10:(.35,0,0),11:(.35,0,0),36:(0,0,0)},False,False),
 ('08-b-homing',{18,26,27,14},(1,1,.5),{**along({27},.35),**along({26},.35)},False,False),
]
# Each guide joins an exploded part to its fitted position.
# Long guide axes on the bed pass through the four support locations.
guides={
 '01-bed':[(i,tuple(N*.85),tuple(N*-.04)) for i in standoff_ids]+[(30,tuple(N*.45),(0,0,0))]+[(i,tuple(-N*.6),(0,0,0)) for i in bed_screws],
 '02-hubs':[(5,(.4,0,0),(0,0,0)),(37,(-.4,0,0),(0,0,0))],
 '04c-motor-screws':[(i,tuple(-N*.35),(0,0,0)) for i in b_screws],
 '06c-screw-detail':[(40,tuple(-N*.5),(0,0,0))],
 '03-holders':[(2,(-.65,0,0),(0,0,0)),(6,(.65,0,0),(0,0,0))],
 '04d-fit-cradle':[(2,(-.4,0,0),(0,0,0)),(6,(.4,0,0),(0,0,0))],
 '04-a-drive':[(38,(.5,0,0),(0,0,0))],
 '04a-cradle-bearing':[(7,tuple(-N*.35),(0,0,0))],
 '04b-cradle-hardware':[(13,tuple(N*.45),(0,0,0)),(20,tuple(N*.4),(0,0,0)),(21,tuple(N*.4),(0,0,0))],
 '05-bed-on-cradle':[(30,tuple(N*.85),(0,0,0))],
 '06-b-drive':[(12,tuple(-N*.3),(0,0,0)),(40,tuple(-N*.9),(0,0,0))],
 '08-a-homing':[],
 '08-b-homing':[],
}
guides['02-hubs'] += [(i,(.65,0,0),(0,0,0)) for i in hub_left]+[(i,(-.65,0,0),(0,0,0)) for i in hub_right]
guides['04-a-drive'] += [(i,(-.35,0,0),(0,0,0)) for i in a_screws]
assembly_guides=json.loads((OUT/'assembly-guides.json').read_text())
projections=json.loads((OUT/'projections.json').read_text())
for name,ids,direction,offsets,show_a,show_b in stages:
 for i,ob in objects.items():ob.hide_render=i not in ids;ob.location=offsets.get(i,(0,0,0))
 a_belt.hide_render=not show_a;b_belt.hide_render=not show_b
 a_belt.location=(-.4,0,0) if name=='04d-fit-cradle' else (0,0,0)
 b_belt.location=tuple(-N*.3) if name=='06-b-drive' else (0,0,0)
 bpy.context.view_layer.update()
 closeups={'04c-motor-screws':b_screws|{13},'08-a-homing':{10,36},'08-b-homing':{18,26},'07-hub-left':{5},'07-hub-right':{37}}
 focus=closeups.get(name,ids)
 scene.render.resolution_x=1100 if name in closeups else 1600
 points=[ob.matrix_world@Vector(v) for i,ob in objects.items() if i in focus for v in ob.bound_box]
 lo=Vector(tuple(min(p[j] for p in points) for j in range(3)));hi=Vector(tuple(max(p[j] for p in points) for j in range(3)));center=(lo+hi)/2
 cam.location=center+Vector(direction).normalized()*9;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
 # Fit both dimensions in the orthographic camera.
 inv=cam.matrix_world.inverted();p=[inv@v for v in points];dx=max(v.x for v in p)-min(v.x for v in p);dy=max(v.y for v in p)-min(v.y for v in p)
 shift=cam.matrix_world.to_quaternion()@Vector(((max(v.x for v in p)+min(v.x for v in p))/2,(max(v.y for v in p)+min(v.y for v in p))/2,0));cam.location+=shift
 camdata.ortho_scale=max(dx,dy*scene.render.resolution_x/scene.render.resolution_y)*(1.35 if name in ('04c-motor-screws','06c-screw-detail') else 1.7 if name=='08-b-homing' else 2.6 if name in closeups else 1.16)
 bpy.context.view_layer.update()
 proj={}
 for i in ids:
  ob=objects[i];pt_local=sum((Vector(v) for v in ob.bound_box),Vector())/8
  if i in (2,6):
   xs=[v.co.x for v in ob.data.vertices];pt_local.x=max(xs) if i==2 else min(xs)
   pt_local=min((v.co for v in ob.data.vertices),key=lambda p:(p-pt_local).length_squared).copy()
  if i in (11,14,15,27):pt_local=min((v.co for v in ob.data.vertices),key=lambda p:(p-pt_local).length_squared).copy()
  pt=ob.matrix_world@pt_local
  if name=='04a-cradle-bearing' and i==14:pt=sum((Vector(v) for v in objects[7].bound_box),Vector())/8
  xy=world_to_camera_view(scene,cam,pt);proj[str(i)]=[xy.x,xy.y]
 projections[name]=proj
 def projected(p):
  xy=world_to_camera_view(scene,cam,p);return [xy.x,xy.y]
 assembly_guides[name]=[]
 for idx,exploded,fitted in guides.get(name,[]):
  ob=objects[idx];center_local=sum((Vector(v) for v in ob.bound_box),Vector())/8
  assembly_guides[name].append([projected(center_local+Vector(exploded)),projected(center_local+Vector(fitted))])
 (OUT/'assembly-guides.json').write_text(json.dumps(assembly_guides,indent=2))
 scene.render.filepath=str(OUT/(name+'.png'))
 if name=='overview':bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'manual/pentos-assembly.blend'),compress=True)
 (OUT/'projections.json').write_text(json.dumps(projections,indent=2))
 only=next((a.split('=',1)[1].split(',') for a in sys.argv if a.startswith('--only=')),None)
 if (only is None or name in only) and ('--force' in sys.argv or not (OUT/(name+'.png')).exists()):bpy.ops.render.render(write_still=True)
 print('FINISHED',name,flush=True)
(OUT/'projections.json').write_text(json.dumps(projections,indent=2))
# Avoid audio shutdown hangs in this system build.
import os;os._exit(0)
