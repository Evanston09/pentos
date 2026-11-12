"""Actual printable 3MF parts, paused-print cutaways, and polarity references."""
import bpy, numpy as np, json, math, os, sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'manual/assets/magnet-preparation';meta=json.loads((ROOT/'manual/slicing/magnet-pause-results.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=bpy.context.scene
s.render.engine='CYCLES';s.render.resolution_x=1500;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.render.film_transparent=True;s.render.image_settings.file_format='PNG';s.render.threads_mode='FIXED';s.render.threads=6
sys.path.insert(0,str(Path(__file__).parent))
from render_style import configure, materials
configure(s)
style=materials()
orange,blue,silver,red,bedmat=[style[k] for k in ('orange','blue','magnet','red','bedmat')]
cd=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',cd);s.collection.objects.link(cam);s.camera=cam;cd.type='ORTHO'
results={}

def cube_clip(ob,lo,hi):
 center=(np.array(lo)+np.array(hi))/2;size=np.array(hi)-np.array(lo)
 bpy.ops.mesh.primitive_cube_add(size=1,location=center*.01);cut=bpy.context.object;cut.dimensions=size*.01;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Actual pocket cutaway','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)

for name,rec in meta.items():
 d=np.load(OUT/f'{name}-print-mesh.npz');verts=d['vertices'];faces=d['faces'];is_a=name.startswith('a-');pmin=np.array(rec['pocket_min']);pmax=np.array(rec['pocket_max']);center=(pmin+pmax)/2
 for detail in (False,True):
  objs=[];mesh=bpy.data.meshes.new(name);mesh.from_pydata((verts*.01).tolist(),[],faces.tolist());mesh.materials.append(orange if is_a else blue);ob=bpy.data.objects.new(name,mesh);s.collection.objects.link(ob);objs.append(ob);ob.color=(0,0,1,1)
  if detail:
   lo=verts.min(0)-1;hi=verts.max(0)+1;hi[2]=pmax[2]-.01
   if is_a:hi[0]=pmax[0]-.05
   else:hi[1]=center[1] # remove front half for a real section through the pocket
   cube_clip(ob,lo,hi)
   mc=center.copy()
   if is_a:mc[2]=pmin[2]+6
   else:mc[2]=pmin[2]+1.5
   bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=.06,depth=.03,location=mc*.01)
   magnet=bpy.context.object;magnet.name='12 x 3 mm magnet';magnet.data.materials.append(silver)
   if is_a:magnet.rotation_euler=(0,math.pi/2,0)
   objs.append(magnet)
   dot=mc.copy()
   if is_a:dot[0]+=1.51;dot[2]+=2
   else:dot[2]-=1.51;dot[1]+=3
   bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.007,depth=.0003,location=dot*.01);mark=bpy.context.object;mark.data.materials.append(red)
   if is_a:mark.rotation_euler=(0,math.pi/2,0)
   objs.append(mark)
   target=mc*.01;span=np.array([32,35,24])*.01 if is_a else np.array([29,28,12])*.01
   pts=[Vector(target+np.array([x,y,z])*span/2) for x in (-1,1) for y in (-1,1) for z in (-1,1)]
   direction=Vector((1,-.8,.9)) if is_a else Vector((.55,1,-.18))
  else:
   mc=center.copy();pts=[Vector(v*.01) for v in verts];direction=Vector((1,-1,1)) if is_a else Vector((.65,-1,1.7))
   target=(verts.min(0)+verts.max(0))*.005
   # Thin footprint plate shows which face is on the build plate.
   xylo=verts[:,:2].min(0)-3;xyhi=verts[:,:2].max(0)+3
   bpy.ops.mesh.primitive_cube_add(size=1,location=((xylo[0]+xyhi[0])*.005,(xylo[1]+xyhi[1])*.005,-.0015));base=bpy.context.object;base.dimensions=((xyhi[0]-xylo[0])*.01,(xyhi[1]-xylo[1])*.01,.002);base.data.materials.append(bedmat);objs.append(base)
  for obj in objs:
   for poly in obj.data.polygons:poly.use_smooth=True
   obj.data.set_sharp_from_angle(angle=math.radians(35))
   mod=obj.modifiers.new('CAD surface normals','WEIGHTED_NORMAL');mod.keep_sharp=True
  cam.location=Vector(target)+direction.normalized()*7;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();inv=cam.matrix_world.inverted();p=[inv@v for v in pts];minx,maxx=min(v.x for v in p),max(v.x for v in p);miny,maxy=min(v.y for v in p),max(v.y for v in p)
  shift=cam.matrix_world.to_quaternion()@Vector(((minx+maxx)/2,(miny+maxy)/2,0));cam.location+=shift;cd.ortho_scale=max(maxx-minx,(maxy-miny)*1500/1200)*1.13;bpy.context.view_layer.update()
  proj={}
  for key,pt in [('pocket',center),('magnet',mc),('mark',dot if detail else center),('base',np.array([center[0],center[1],0]))]:
   xy=world_to_camera_view(s,cam,Vector(pt*.01));proj[key]=[xy.x,xy.y]
  key=name+('-detail' if detail else '-full');results[key]=proj;s.render.filepath=str(OUT/(key+'.png'));bpy.ops.render.render(write_still=True);print('RENDERED',key,flush=True)
  for o in objs:bpy.data.objects.remove(o,do_unlink=True)
(OUT/'render-projections.json').write_text(json.dumps(results,indent=2));os._exit(0)
