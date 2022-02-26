from os.path import dirname, abspath, join

from es_odm import __version__

CURRENT_PATH = dirname(abspath(__file__))

current_version = __version__
version_list = current_version.split('.')
version_list[-1] = str(int(version_list[-1]) + 1)
new_version = '.'.join(version_list)

with open(join(CURRENT_PATH, "./es_odm/version.py"), 'w') as fn:
    fn.write(f"VERSION = '{new_version}'")
