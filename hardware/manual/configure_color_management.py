"""Prepare the installed Blender OCIO config for this system's older OCIO library."""
from pathlib import Path
import re,tempfile
source=Path('/usr/share/blender/5.2/datafiles/colormanagement/config.ocio')
s=source.read_text()
# Blender's bundled LUTs work with OCIO 2.4; only its metadata schema is newer.
s=s.replace('ocio_profile_version: 2.5','ocio_profile_version: 2.4')
s=re.sub(r'^    interop_id:.*\n','',s,flags=re.M)
s=re.sub(r'^    interchange:\n(?:      .*\n)+','',s,flags=re.M)
s=s.replace('search_path: "icc:luts:filmic"','search_path: "'+':'.join(str(source.parent/a) for a in ['icc','luts','filmic'])+'"')
target=Path(tempfile.gettempdir())/'pentos-blender-compatible.ocio';target.write_text(s)
print(target)
