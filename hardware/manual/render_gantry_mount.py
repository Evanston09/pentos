"""Ender gantry mounting: assembled mechanism and enlarged countersunk joint."""
from pathlib import Path
import bpy,sys,json,math,os
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'manual/assets/blender';sys.path.insert(0,str(Path(__file__).parent))
from render_style import configure,materials,material
scene=bpy.context.scene;configure(scene);style=materials();scene.render.engine='CYCLES';scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.threads_mode='FIXED';scene.render.threads=6
original=[o for o in scene.objects if o.type=='MESH'];objects={int(o['cad_index']):o for o in original if 'cad_index' in o}
for o in original:o.hide_render=False;o.location=(0,0,0)
meta=json.loads((ROOT/'manual/assets/ender-mount-registration.json').read_text());data=np.load(ROOT/'manual/assets/ender-mount-meshes.npz');shift=np.array(meta['translation_mm']);feet=np.array(meta['foot_centers_mm'])
gantry_mat=material('Ender painted gantry','#3B4047',.45,.55);knob_mat=material('Original leveling wheel','#26292C',.7)
def cv(v):return np.column_stack((v[:,0],-v[:,2],v[:,1]))*.01
def add_mesh(idx,name,verts,faces,mat):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts.tolist(),[],faces.tolist());mesh.materials.append(mat);mesh.update();ob=bpy.data.objects.new(name,mesh);scene.collection.objects.link(ob);ob['cad_index']=idx;objects[idx]=ob
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.remove_doubles(threshold=.000005);bpy.ops.object.mode_set(mode='OBJECT');ob.select_set(False)
 for p in mesh.polygons:p.use_smooth=True
 mesh.set_sharp_from_angle(angle=math.radians(35));m=ob.modifiers.new('CAD normals','WEIGHTED_NORMAL');m.keep_sharp=True
 return ob
add_mesh(100,'Ender Y gantry',cv(data['gantry_vertices']+shift),data['gantry_faces'],gantry_mat)
axis=np.array(meta['knob_source_axis_mm'])
for k,(x,z) in enumerate(feet):
 delta=shift.copy();delta[0]+=x-(axis[0]+shift[0]);delta[2]+=z-(axis[2]+shift[2]);add_mesh(104+k,'Original leveling knob '+str(k+1),cv(data['knob_vertices']+delta),data['knob_faces'],knob_mat)
def countersunk_screw(idx,x,y,top):
 # Stock M4 countersunk bed screw: 90-degree head matching the CAD seat.
 pieces=[]
 bpy.ops.mesh.primitive_cone_add(vertices=64,radius1=.020,radius2=.035,depth=.015,location=(x,y,top-.0075));head=bpy.context.object;head.data.materials.append(style['metal']);pieces.append(head)
 for angle in (0,math.pi/2):
  bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,top-.003));cut=bpy.context.object;cut.dimensions=(.043,.009,.009);cut.rotation_euler[2]=angle;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  bpy.context.view_layer.objects.active=head;m=head.modifiers.new('Cross recess','BOOLEAN');m.object=cut;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.0165,depth=.285,location=(x,y,top-.1575));core=bpy.context.object;core.data.materials.append(style['metal']);pieces.append(core)
 # M4 x 0.7 thread, with a 4 mm major diameter. Overall drawn length is 30 mm.
 verts=[];faces=[];length=.282;pitch=.007;turns=length/pitch;steps=math.ceil(turns*28)
 for j in range(steps+1):
  a=2*math.pi*turns*j/steps;zz=top-.017-length*j/steps
  for r,dz in [(.0165,-.0027),(.020,0),(.0165,.0027)]:verts.append((x+r*math.cos(a),y+r*math.sin(a),zz+dz))
 for j in range(steps):
  for p in range(2):faces.append((j*3+p,(j+1)*3+p,(j+1)*3+p+1,j*3+p+1))
 mesh=bpy.data.meshes.new('M4 thread');mesh.from_pydata(verts,[],faces);mesh.materials.append(style['metal']);thread=bpy.data.objects.new('M4 thread',mesh);scene.collection.objects.link(thread);pieces.append(thread)
 bpy.ops.object.select_all(action='DESELECT')
 for p in pieces:p.select_set(True)
 bpy.context.view_layer.objects.active=head;bpy.ops.object.join();head.name='Original M4 countersunk bed screw '+str(idx-109);head['cad_index']=idx;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);objects[idx]=head
 for p in head.data.polygons:p.use_smooth=True
 head.data.set_sharp_from_angle(angle=math.radians(35));m=head.modifiers.new('Screw normals','WEIGHTED_NORMAL');m.keep_sharp=True
for k,(x,z) in enumerate(feet):countersunk_screw(110+k,x*.01,-z*.01,meta['holder_top_y_mm']*.01)
cam=scene.camera;cam.data.type='ORTHO';projected=json.loads((OUT/'projections.json').read_text());guides=json.loads((OUT/'assembly-guides.json').read_text())
def point(pt):
 p=world_to_camera_view(scene,cam,Vector(pt));return [p.x,p.y]
def nearest(idx,pt):
 ob=objects[idx];q=min((ob.matrix_world@v.co for v in ob.data.vertices),key=lambda v:(v-Vector(pt)).length_squared);return q

def fit(direction,pts):
 lo=Vector(tuple(min(v[j] for v in pts) for j in range(3)));hi=Vector(tuple(max(v[j] for v in pts) for j in range(3)));center=(lo+hi)/2
 cam.location=center+Vector(direction).normalized()*9;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();iv=cam.matrix_world.inverted();q=[iv@v for v in pts]
 x1,x2=min(p.x for p in q),max(p.x for p in q);y1,y2=min(p.y for p in q),max(p.y for p in q)
 cam.location+=cam.matrix_world.to_quaternion()@Vector(((x1+x2)/2,(y1+y2)/2,0));cam.data.ortho_scale=max(x2-x1,(y2-y1)*scene.render.resolution_x/scene.render.resolution_y)*1.12;bpy.context.view_layer.update()
for name in ['09-mounted','09-mount-detail']:
 detail=name.endswith('detail');scene.render.resolution_x=1100 if detail else 1600;scene.render.resolution_y=1400 if detail else 1250
 for o in original:o.hide_render=detail and o!=objects[15];o.location=(0,0,0)
 for idx in (100,104,105,106,107,110,111,112,113):objects[idx].hide_render=detail and idx not in (100,104,110);objects[idx].location=(0,0,0)
 x,z=feet[0];anchor=Vector((x*.01,-z*.01,meta['holder_top_y_mm']*.01))
 if detail:
  objects[110].location.z=.20;objects[104].location.z=-.16
  center=Vector((anchor.x,anchor.y,-.04));size=Vector((.82,.82,.98));pts=[center+Vector((a*size.x,b*size.y,c*size.z))/2 for a in (-1,1) for b in (-1,1) for c in (-1,1)]
  fit((1,1,1.2),pts)
 else:
  pts=[o.matrix_world@Vector(v) for o in scene.objects if o.type=='MESH' and not o.hide_render for v in o.bound_box];fit((1,1,1.1),pts)
 p={}
 for idx in (100,104,105,106,110,15):
  ob=objects[idx];target=anchor if idx==110 else anchor+Vector((.06,-.06,0)) if idx==15 else anchor+Vector((0,.18,-.2)) if idx==104 else Vector((.4,-.55,0))
  if idx==105:target=Vector((feet[1,0]*.01-.20,-feet[1,1]*.01-.20,-.09))
  if idx==106:target=Vector((feet[2,0]*.01+.20,-feet[2,1]*.01+.20,-.09))
  if idx==110:target+=ob.location
  p[str(idx)]=point(nearest(idx,target))
 projected[name]=p;guides[name]=[]
 if detail:
  guides[name]=[[point(anchor+Vector((0,0,.2))),point(anchor)], [point(anchor+Vector((0,0,-.48))),point(anchor+Vector((0,0,-.12)))]]
 else:bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'manual/pentos-mounted.blend'),compress=True)
 scene.render.filepath=str(OUT/(name+'.png'))
 if not any(a.startswith('--only=') for a in sys.argv) or '--only='+name in sys.argv:
  bpy.ops.render.render(write_still=True);print('RENDERED',name,flush=True)
(OUT/'projections.json').write_text(json.dumps(projected,indent=2));(OUT/'assembly-guides.json').write_text(json.dumps(guides,indent=2));os._exit(0)
