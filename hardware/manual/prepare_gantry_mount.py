"""Mesh the supplied Ender parts and register the four stock mounting axes."""
from pathlib import Path
import json,hashlib
import numpy as np
from OCP.STEPControl import STEPControl_Reader
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE,TopAbs_REVERSED
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopLoc import TopLoc_Location
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'manual/assets';saved={};sources={}
for name,file in [('gantry','Creality-Ender3-V2 - Y-Gantry.step'),('knob','Creality-Ender3-V2 - Bed Level Knob.step')]:
 path=ROOT/'manual'/file;r=STEPControl_Reader();r.ReadFile(str(path));r.TransferRoots();sh=r.OneShape();BRepMesh_IncrementalMesh(sh,.10,False,.18,True)
 verts=[];faces=[];holes=[];e=TopExp_Explorer(sh,TopAbs_FACE)
 while e.More():
  face=TopoDS.Face_s(e.Current());a=BRepAdaptor_Surface(face)
  if a.GetType()==GeomAbs_Cylinder:
   cy=a.Cylinder();ax=cy.Axis();p=ax.Location()
   if abs(cy.Radius()-2.025)<.001 and abs(ax.Direction().Y())>.99:holes.append([p.X(),p.Z()])
  loc=TopLoc_Location();tri=BRep_Tool.Triangulation_s(face,loc)
  if tri:
   first=len(verts)
   for j in range(1,tri.NbNodes()+1):
    p=tri.Node(j).Transformed(loc.Transformation());verts.append([p.X(),p.Y(),p.Z()])
   for j in range(1,tri.NbTriangles()+1):
    aa,b,c=tri.Triangle(j).Get()
    if face.Orientation()==TopAbs_REVERSED:b,c=c,b
    faces.append([first+aa-1,first+b-1,first+c-1])
  e.Next()
 v=np.array(verts);saved[name+'_vertices']=v;saved[name+'_faces']=np.array(faces)
 if name=='gantry':gantry_holes=np.unique(np.round(holes,7),axis=0);top=float(v[:,1].max());bottom=float(v[:,1].min())
 sources[name]=dict(file=file,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bounds=[v.min(0).tolist(),v.max(0).tolist()])
# These centers are measured from the radius-2 foot-hole loops in Pentos.step.
feet=np.array([[-84.18666808,-85.50753163],[-84.18666808,84.49246837],[85.81333192,-85.50753163],[85.81333192,84.49246837]])
base_y=2.056934;foot_top=10.056934
assert len(gantry_holes)==4
shift=np.array([feet[:,0].mean()-gantry_holes[:,0].mean(),base_y-top,feet[:,1].mean()-gantry_holes[:,1].mean()])
matched=gantry_holes+shift[[0,2]];assert np.max(abs(matched-feet))<1e-5
knob_axis=np.array([-115.93554200955,0,-109.236982975513]);knob_top=saved['knob_vertices'][:,1].max()
assert abs((knob_top+shift[1])-(bottom+shift[1]))<1e-5
# Verify all four fitted countersinks against the actual assembly mesh.
assembly=np.load(OUT/'meshes.npz')
for x,z in feet:
 v=assembly['v15' if x<0 else 'v11'];r=np.linalg.norm(v[:,[0,2]]-[x,z],axis=1)
 assert np.any((abs(r-2)<1e-5)&(abs(v[:,1]-8.556934)<1e-5))
 assert np.any((abs(r-3.5)<1e-5)&(abs(v[:,1]-foot_top)<1e-5))
meta=dict(sources=sources,translation_mm=shift.tolist(),foot_centers_mm=feet.tolist(),holder_bottom_y_mm=base_y,holder_top_y_mm=foot_top,gantry_top_y_mm=base_y,gantry_bottom_y_mm=bottom+shift[1],knob_source_axis_mm=knob_axis.tolist(),gantry_thickness_mm=top-bottom,countersink=dict(shaft_diameter_mm=4,head_diameter_mm=7,included_angle_deg=90),illustrative_screw_overall_length_mm=30)
np.savez_compressed(OUT/'ender-mount-meshes.npz',**saved)
(OUT/'ender-mount-registration.json').write_text(json.dumps(meta,indent=2))
print(json.dumps(meta,indent=2))
