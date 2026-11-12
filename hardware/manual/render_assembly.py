"""Render the actual Onshape STEP assembly. Requires cadquery-ocp<8, vtk, numpy."""
from pathlib import Path
import json
import numpy as np
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TDataStd import TDataStd_Name
from OCP.TopLoc import TopLoc_Location
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
import vtk
from vtk.util.numpy_support import numpy_to_vtk
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'manual/assets'; OUT.mkdir(exist_ok=True)
cache=OUT/'meshes.npz'
def get_name(l):
 n=TDataStd_Name()
 return n.Get().ToExtString() if l.FindAttribute(TDataStd_Name.GetID_s(),n) else 'part'
if not cache.exists():
 r=STEPCAFControl_Reader(); d=TDocStd_Document(TCollection_ExtendedString('doc')); r.ReadFile(str(ROOT/'Pentos.step')); r.Transfer(d)
 s=XCAFDoc_DocumentTool.ShapeTool_s(d.Main()); roots=TDF_LabelSequence(); s.GetFreeShapes(roots); parts=[]
 def walk(label,loc=TopLoc_Location(),inst_name=None):
  if s.IsReference_s(label):
   ref=TDF_Label(); s.GetReferredShape_s(label,ref)
   return walk(ref,loc.Multiplied(s.GetLocation_s(label)),get_name(label))
  seq=TDF_LabelSequence(); s.GetComponents_s(label,seq)
  if seq.Length():
   for i in range(1,seq.Length()+1): walk(seq.Value(i),loc)
   return
  shape=s.GetShape_s(label).Moved(loc); BRepMesh_IncrementalMesh(shape,0.22,False,0.35,True)
  verts=[]; faces=[]; exp=TopExp_Explorer(shape,TopAbs_FACE)
  while exp.More():
   face=TopoDS.Face_s(exp.Current()); floc=TopLoc_Location(); tri=BRep_Tool.Triangulation_s(face,floc)
   if tri:
    offset=len(verts)
    for j in range(1,tri.NbNodes()+1):
     p=tri.Node(j).Transformed(floc.Transformation()); verts.append((p.X(),p.Y(),p.Z()))
    for j in range(1,tri.NbTriangles()+1):
     a,b,c=tri.Triangle(j).Get()
     if face.Orientation()==TopAbs_REVERSED:b,c=c,b
     faces.append((a-1+offset,b-1+offset,c-1+offset))
   exp.Next()
  if verts:parts.append((inst_name or get_name(label),np.array(verts),np.array(faces)))
 for i in range(1,roots.Length()+1):walk(roots.Value(i))
 data={}
 for i,(name,v,f) in enumerate(parts):data[f'v{i}']=v;data[f'f{i}']=f;data[f'n{i}']=name
 np.savez_compressed(cache,**data)
else:
 data=np.load(cache); parts=[(str(data[f'n{i}']),data[f'v{i}'],data[f'f{i}']) for i in range(len(data.files)//3)]
# Onshape assembly uses Y up; normalize to Z up for page illustrations.
parts=[(n,np.column_stack((v[:,0],-v[:,2],v[:,1])),f) for n,v,f in parts]
meta=[]
for i,(n,v,f) in enumerate(parts):meta.append(dict(id=i,name=n,min=v.min(0).round(2).tolist(),max=v.max(0).round(2).tolist()))
(OUT/'parts.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta,indent=2),flush=True)

def group(n):
 if 'Holder' in n:return 'holder'
 if 'Craddle' in n:return 'cradle'
 if 'V-Axis Base' in n:return 'rotor'
 if any(k in n for k in ['Buildplate','Heatbed','Spacer','REV-']):return 'bed'
 if 'Carriage' in n:return 'hardware'
 if 'Nema' in n:return 'motor'
 if 'Sensor' in n or 'Magnet' in n:return 'sensor'
 return 'hardware'
colors={'holder':'#14a5a0','cradle':'#eaa548','rotor':'#4a89d0','bed':'#c4ccd3','carriage':'#647582','motor':'#333d49','sensor':'#b16563','hardware':'#9daab4'}
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
projections={}
def render(filename,groups=None,explode=False,direction=(1,-1,0.8),highlight=None):
 ren=vtk.vtkRenderer();ren.SetBackground(0.958,0.969,0.977)
 allverts=[]
 for i,(n,v,f) in enumerate(parts):
  g=group(n)
  if groups and g not in groups:continue
  v=v.copy()
  if explode:
   shift={'holder':(0,0,-15),'cradle':(0,0,28),'rotor':(0,0,65),'bed':(0,0,100),'motor':(0,-30,0)}.get(g,(0,0,0));v+=shift
  pts=vtk.vtkPoints();pts.SetData(numpy_to_vtk(v,deep=True));cells=vtk.vtkCellArray()
  for face in f:
   cells.InsertNextCell(3)
   for idx in face:cells.InsertCellPoint(int(idx))
  poly=vtk.vtkPolyData();poly.SetPoints(pts);poly.SetPolys(cells)
  normals=vtk.vtkPolyDataNormals();normals.SetInputData(poly);normals.SetFeatureAngle(40)
  mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort());actor=vtk.vtkActor();actor.SetMapper(mapper)
  actor.GetProperty().SetColor(rgb(colors[g]));actor.GetProperty().SetSpecular(.25);actor.GetProperty().SetSpecularPower(24)
  if highlight and g not in highlight:actor.GetProperty().SetOpacity(.16)
  ren.AddActor(actor);allverts.append(v)
 win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.AddRenderer(ren);win.SetSize(1800,1500);win.SetMultiSamples(8)
 bounds=np.concatenate(allverts);center=(bounds.min(0)+bounds.max(0))/2;span=np.linalg.norm(bounds.max(0)-bounds.min(0))
 cam=ren.GetActiveCamera();cam.SetPosition(*(center+np.array(direction)*span*2));cam.SetFocalPoint(*center);cam.SetViewUp(0,0,1);cam.ParallelProjectionOn();ren.ResetCamera();cam.Zoom(1.13);ren.ResetCameraClippingRange()
 win.Render()
 proj={}
 for idx in [9,11,12,13,14,15,27,34,38]:
  n,v,f=parts[idx];p=v.mean(0)
  if explode:p=p+np.array({'holder':(0,0,-15),'cradle':(0,0,28),'rotor':(0,0,65),'bed':(0,0,100),'motor':(0,-30,0)}.get(group(n),(0,0,0)))
  ren.SetWorldPoint(*p,1);ren.WorldToDisplay();dx,dy,dz=ren.GetDisplayPoint();proj[str(idx)]=[dx/1800,dy/1500]
 projections[filename]=proj
 snap=vtk.vtkWindowToImageFilter();snap.SetInput(win);snap.Update();writer=vtk.vtkPNGWriter();writer.SetFileName(str(OUT/filename));writer.SetInputConnection(snap.GetOutputPort());writer.Write();win.Finalize()
for name,kw in [
 ('assembly.png',{}),('rear.png',dict(direction=(-1,1,.7))),('exploded.png',dict(explode=True)),
 ('holders.png',dict(highlight=['holder','carriage'])),('cradle.png',dict(highlight=['cradle','hardware'])),
 ('rotation.png',dict(highlight=['rotor','motor','hardware'],direction=(1,-1,-.7))),
 ('bed.png',dict(highlight=['bed','rotor'])),('homing.png',dict(highlight=['sensor'],direction=(-1,1,.6)))]:
 render(name,**kw);print('Rendered',name,flush=True)

(OUT/'projections.json').write_text(json.dumps(projections,indent=2))
