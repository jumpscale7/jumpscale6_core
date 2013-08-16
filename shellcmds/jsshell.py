import sys
sys.path.insert(0,"lib")
from OpenWizzy import *

o.application.appname = "owshell"
o.application.start()

o.application.shellconfig.interactive=True

from IPython import embed
embed()

