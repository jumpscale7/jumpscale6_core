import sys
sys.path.insert(0,"lib")

from JumpScale import j

j.application.appname = "jsshell"
j.application.start()

j.application.shellconfig.interactive=True

from IPython import embed
embed()

