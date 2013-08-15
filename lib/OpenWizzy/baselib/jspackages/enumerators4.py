from OpenWizzy.core.baseclasses import BaseEnumeration

class DependencyType4(BaseEnumeration):
    """
    One of two constants: runtime and build.
    When a package has a runtime dependency on another package it means the first package cannot operate properly without the second package being installed.
    When a package has a build dependency on another package it means the first package cannot be build without the second package being installed.
    The second package typically is some build tool like gcc.
    #@todo doc
    """
    pass

DependencyType4.registerItem('runtime')
DependencyType4.registerItem('build')
DependencyType4.finishItemRegistration()


class VListType4(BaseEnumeration):
    """
    #@todo doc
    """
    pass

VListType4.registerItem('server')
VListType4.registerItem('client')
VListType4.finishItemRegistration()


class ACLPermission4(BaseEnumeration):
    """
    #@todo doc
    """
    pass
ACLPermission4.registerItem('R')

ACLPermission4.registerItem('W') ##only write access? for rsync that is not possible, no?
ACLPermission4.registerItem('RW')
ACLPermission4.finishItemRegistration()


class QPackageState4(BaseEnumeration):
    """
    The states a QPackage can find itself in.
    """
    pass

QPackageState4.registerItem('ERROR')
QPackageState4.registerItem('OK')
QPackageState4.finishItemRegistration()

class QPackageQualityLevelType4(BaseEnumeration):
    """ QPackage quality level """
    def __repr__(self):
        return str(self)
        
QPackageQualityLevelType4.registerItem('trunk')
QPackageQualityLevelType4.registerItem('test')
QPackageQualityLevelType4.registerItem('stable')
QPackageQualityLevelType4.registerItem('beta')
QPackageQualityLevelType4.registerItem('unstable')
QPackageQualityLevelType4.finishItemRegistration()