from JumpScale import j
import JumpScale.baselib.actions
import JumpScale.baselib.bitbucket
import JumpScale.baselib.mercurial
import JumpScale.baselib.taskletengine
import JumpScale.baselib.blobstor
import JumpScale.baselib.cloudsystemfs

from .JPackageClient import JPackageClient
from .JPackageIClient import JPackageIClient
from .ReleaseMgmt import ReleaseMgmt
from .JPackageMetadataScanner import JPackageMetadataScanner


j.packages=JPackageClient()

j.packagesi=JPackageIClient()

j.packages.releaseMgmt=ReleaseMgmt()
j.packages.metadataScanner=JPackageMetadataScanner()