"""Shared, neutral studio rendering for the CAD assembly and print sections."""
import bpy
from mathutils import Vector

def linear(hexcolor):
 rgb=[int(hexcolor[i:i+2],16)/255 for i in (1,3,5)]
 return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb)

def material(name,color,rough=.45,metal=0,texture=False):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*linear(color),1)
 nodes=m.node_tree.nodes;links=m.node_tree.links;bs=nodes.get('Principled BSDF')
 bs.inputs['Base Color'].default_value=(*linear(color),1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
 bevel=nodes.new('ShaderNodeBevel');bevel.inputs['Radius'].default_value=.00065;bevel.samples=3
 if texture:
  geo=nodes.new('ShaderNodeNewGeometry');info=nodes.new('ShaderNodeObjectInfo')
  dot=nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';links.new(geo.outputs['Position'],dot.inputs[0]);links.new(info.outputs['Color'],dot.inputs[1])
  spacing=nodes.new('ShaderNodeMath');spacing.operation='MULTIPLY';spacing.inputs[1].default_value=3141.592654;links.new(dot.outputs['Value'],spacing.inputs[0])
  wave=nodes.new('ShaderNodeMath');wave.operation='SINE';links.new(spacing.outputs[0],wave.inputs[0])
  bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.000025
  links.new(wave.outputs[0],bump.inputs['Height']);links.new(bevel.outputs['Normal'],bump.inputs['Normal']);links.new(bump.outputs['Normal'],bs.inputs['Normal'])

 else:links.new(bevel.outputs['Normal'],bs.inputs['Normal'])
 return m

def materials():
 return dict(blue=material('Printed blue','#2D628F',.53,texture=True),orange=material('Printed orange','#C47026',.53,texture=True),metal=material('Machined silver','#C5C9CE',.26,1),black=material('Motor housing','#292D33',.42,.2),plate=material('Gold build surface','#CEAD61',.42,.65),heater=material('Heatbed','#373A3F',.6),silicone=material('Silicone','#AC6847',.82),sensor=material('Sensor housing','#282B2F',.6),magnet=material('Nickel magnet','#C0C3C7',.21,1),beltmat=material('Belt rubber','#222426',.83),red=material('Polarity mark','#A92B23',.65),bedmat=material('Build plane','#D8DBDE',.75))

def configure(scene):
 scene.render.use_freestyle=False
 scene.cycles.samples=48;scene.cycles.use_denoising=True
 scene.cycles.max_bounces=8
 scene.world.use_nodes=True;bg=scene.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.65,.65,.65,1);bg.inputs['Strength'].default_value=.65
 scene.view_settings.view_transform='AgX'
 scene.view_settings.look='AgX - Medium High Contrast'
 scene.view_settings.exposure=-1.1
 for ob in list(bpy.data.objects):
  if ob.type=='LIGHT':bpy.data.objects.remove(ob,do_unlink=True)
 for name,loc,power,size in [('Key',(1,-3,5),550,3),('Fill',(-3,-1,2),150,5),('Rim',(2,3,4),400,3),('Underside',(1,-3,-3),140,4)]:
  d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,.5))-o.location).to_track_quat('-Z','Y').to_euler()
