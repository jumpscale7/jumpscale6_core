from JumpScale import j
from . import AbstractPackage

class Package(AbstractPackage):
    def install(self, *args, **kwargs):
        j.packages.native.install(self.name)

