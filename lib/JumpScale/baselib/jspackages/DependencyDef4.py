from JumpScale import j
from JumpScale.core.baseclasses import BaseType
from enumerators4 import DependencyType4

class DependencyDef4(BaseType):
 
    name=j.basetype.string(doc="official name of owpackage, is part of unique identifier of owpackage")
    minversion=j.basetype.string(doc="Version of owpackage normally x.x format, is part of unique identifier of owpackage", allow_none=True)
    maxversion=j.basetype.string(doc="Version of owpackage normally x.x format, is part of unique identifier of owpackage", allow_none=True)
    domain=j.basetype.string(doc="url of domain, is part of unique identifier of owpackage")
    supportedPlatforms=j.basetype.list(doc="supported platforms, see j.enumerators.PlatformType.")
    dependencytype= j.basetype.enumeration(DependencyType4, doc='Type of the Dependency', default=DependencyType4.RUNTIME)

    def __str__(self):
        return "%s_%s %s-%s %s for platforms: %s" % (self.domain, self.name, self.minversion, self.maxversion, self.dependencytype, str(self.supportedPlatforms))

    def __repr__(self):
        return self.__str__()