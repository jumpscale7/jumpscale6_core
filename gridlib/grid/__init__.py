from OpenWizzy import o
import OpenWizzy.baselib.serializers
from GridFactory import GridFactory

class Empty():
	pass

class Empty():
	pass

if not  o.__dict__.has_key("core"):
	o.core=Empty()

o.core.grid=GridFactory()

