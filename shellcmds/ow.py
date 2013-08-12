from OpenWizzy import *

o.application.appname = "ow"
o.application.start()
o.application.shellconfig.interactive = True

from IPython import embed
embed()

