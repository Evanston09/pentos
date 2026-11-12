"""Re-slice the saved Prusa projects and check the pause precedes pocket closure."""
from pathlib import Path
import json,re,subprocess
ROOT=Path(__file__).resolve().parents[2];WORK=ROOT/'tmp/pdfs/magnet-slicing';WORK.mkdir(parents=True,exist_ok=True)
meta=json.loads((ROOT/'manual/slicing/magnet-pause-results.json').read_text())
for name,rec in meta.items():
 target=WORK/f'{name}-pause-verified.gcode'
 subprocess.run(['prusa-slicer','--export-gcode','--output',str(target),str(ROOT/f'manual/slicing/{name}-magnet-pause.3mf')],check=True,stdout=subprocess.DEVNULL)
 lines=target.read_text().splitlines();pause=lines.index('M601');layer=sum(l==';LAYER_CHANGE' for l in lines[:pause]);z=float([l[3:] for l in lines[:pause] if l.startswith(';Z:')][-1])
 assert layer==rec['preview_layer'] and abs(z-rec['pause_z'])<1e-6,(name,layer,z)
 start=max(i for i,l in enumerate(lines[:pause]) if l==';LAYER_CHANGE')
 assert not any(l.startswith('G1 ') and ' X' in l and ' E' in l for l in lines[start:pause]),'Extrusion before pause'
 end=next((i for i in range(pause+1,len(lines)) if lines[i]==';LAYER_CHANGE'),len(lines))
 assert ';TYPE:Bridge infill' in lines[pause:end],'No bridge after pause'
 assert '; layer_height = 0.2' in lines and '; first_layer_height = 0.2' in lines
 print(f'{name}: pause verified BEFORE Preview layer {layer}, Z {z:.2f}; closing bridges follow.')
