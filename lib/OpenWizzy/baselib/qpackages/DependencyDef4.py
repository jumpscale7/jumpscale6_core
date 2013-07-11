from OpenWizzy import o
from OpenWizzy.core.baseclasses import BaseType
from enumerators4 import DependencyType4

class DependencyDef4(BaseType):
 
    name=o.basetype.string(doc="official name of owpackage, is part of unique identifier of owpackage")
    minversion=o.basetype.string(doc="Version of owpackage normally x.x format, is part of unique identifier of owpackage", allow_none=True)
    maxversion=o.basetype.string(doc="Version of owpackage normally x.x format, is part of unique identifier of owpackage", allow_none=True)
    domain=o.basetype.string(doc="url of domain, is part of unique identifier of owpackage")
    supportedPlatforms=o.basetype.list(doc="supported platforms, see o.enumerators.PlatformType.")
    dependencytype= o.basetype.enumeration(DependencyType4, doc='Type of the Dependency', default=DependencyType4.RUNTIME)

    def __str__(self):
        return "%s_%s %s-%s %s for platforms: %s" % (self.domain, self.name, self.minversion, self.maxversion, self.dependencytype, str(self.supportedPlatforms))

    def __repr__(self):
        return self.__str__()