from OpenWizzy import o
from ubuntu.Ubuntu import Ubuntu

class Empty:
	pass

o.system.platform=Empty()

o.system.platform.ubuntu=Ubuntu()
# o.system.platformtype.ubuntu=Ubuntu