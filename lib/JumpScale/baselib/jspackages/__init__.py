from JumpScale import j
import JumpScale.baselib.actions
import JumpScale.baselib.bitbucket
import JumpScale.baselib.mercurial
import JumpScale.baselib.taskletengine
import JumpScale.baselib.blobstor
import JumpScale.baselib.cloudsystemfs

from .QPackageClient4 import QPackageClient4
from .QPackageIClient4 import QPackageIClient4
from .ReleaseMgmt import ReleaseMgmt
from .QPackageMetadataScanner import QPackageMetadataScanner


j.packages=QPackageClient4()

j.packagesi=QPackageIClient4()

j.packages.releaseMgmt=ReleaseMgmt()
j.packages.metadataScanner=QPackageMetadataScanner()


