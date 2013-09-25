from JumpScale import j
from . import AbstractPackage

class Package(AbstractPackage):
    def install(self, *args, **kwargs):
         j.system.platform.ubuntu.install(self.name)

