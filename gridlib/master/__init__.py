from JumpScale import j

from MasterObjects import *
from Master import *


class Empty():
    pass

j.core.master = Empty()
j.core.master = MasterServerFactory()
j.core.master.models = MasterObjectsFactory()
