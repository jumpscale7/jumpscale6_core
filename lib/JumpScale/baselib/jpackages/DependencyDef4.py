from JumpScale import j
from JumpScale.core.baseclasses import BaseType
from enumerators4 import DependencyType4
import importlib

class DependencyDef4(BaseType):
 
    name=j.basetype.string(doc="official name of jpackages, is part of unique identifier of jpackages")
    minversion=j.basetype.string(doc="Version of jpackages normally x.x format, is part of unique identifier of jpackages", allow_none=True)
    maxversion=j.basetype.string(doc="Version of jpackages normally x.x format, is part of unique identifier of jpackages", allow_none=True)
    domain=j.basetype.string(doc="url of domain, is part of unique identifier of jpackages")
    supportedPlatforms=j.basetype.list(doc="supported platforms, see j.enumerators.PlatformType.")
    dependencytype= j.basetype.enumeration(DependencyType4, doc='Type of the Dependency', default=DependencyType4.RUNTIME)

    def __str__(self):
        return "%s_%s %s-%s %s for platforms: %s" % (self.domain, self.name, self.minversion, self.maxversion, self.dependencytype, str(self.supportedPlatforms))

    def __repr__(self):
        return self.__str__()

    def getPackage(self, platform, returnNoneIfNotFound):
        if self.dependencytype in (DependencyType4.RUNTIME, DependencyType4.BUILD):
            return j.packages.jumpscale.findNewest(domain=self.domain, name=self.name, minversion=self.minversion, maxversion=self.maxversion, platform=platform, returnNoneIfNotFound=returnNoneIfNotFound)
        else:
            module = importlib.import_module('JumpScale.baselib.jpackages.dependencytypes.%s' % self.dependencytype)
            return module.Package(self.name, self.minversion, self.maxversion)
