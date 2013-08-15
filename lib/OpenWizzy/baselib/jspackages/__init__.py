from OpenWizzy import o
import OpenWizzy.baselib.actions
import OpenWizzy.baselib.bitbucket
import OpenWizzy.baselib.mercurial
import OpenWizzy.baselib.taskletengine
import OpenWizzy.baselib.blobstor
import OpenWizzy.baselib.cloudsystemfs

from .QPackageClient4 import QPackageClient4
from .QPackageIClient4 import QPackageIClient4
from .ReleaseMgmt import ReleaseMgmt
from .QPackageMetadataScanner import QPackageMetadataScanner


o.packages=QPackageClient4()

o.packagesi=QPackageIClient4()

o.packages.releaseMgmt=ReleaseMgmt()
o.packages.metadataScanner=QPackageMetadataScanner()


