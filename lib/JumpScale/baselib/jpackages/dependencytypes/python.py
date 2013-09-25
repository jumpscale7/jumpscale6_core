from JumpScale import j
from . import AbstractPackage

class Package(AbstractPackage):
    def install(self, *args, **kwargs):
        minversion = self.minversion
        maxversion = self.maxversion
        version = []
        if minversion:
        	version.append('>=%s' % minversion)
        if maxversion:
        	version.append('<=%s' % maxversion)

        version = ','.join(version)

        j.system.platform.python.install(self.name, version)

