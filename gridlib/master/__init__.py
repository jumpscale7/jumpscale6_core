from OpenWizzy import o

from MasterObjects import *
from Master import *

class Empty():
	pass

o.core.master=Empty()
o.core.master=MasterServerFactory()
o.core.master.models=MasterObjectsFactory()
