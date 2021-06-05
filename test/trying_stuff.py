import sysconfig
import site
from pprint import pprint
import os

print(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

print( os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..')) )

exit(1)

dirs_dict = {
    'sys_dirs': sysconfig.get_paths()["purelib"],
    'usr_dirs': site.getusersitepackages(),
    'site_dirs': site.getsitepackages()
}

dirs = []
for v in dirs_dict.values():
    if isinstance(v, list):
        dirs.extend(v)
    else:
        dirs.append(v)
pprint(dirs)
