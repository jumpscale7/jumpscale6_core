from JumpScale import j
from . import AbstractPackage

class Package(AbstractPackage):
    def install(self, *args, **kwargs):
        # TODO do something with versions
        j.packages.python.install(self.name)

