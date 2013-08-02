from OpenWizzy import *

o.application.appname = "owshell"
o.application.start()

o.application.shellconfig.interactive=True

from IPython import embed
embed()

