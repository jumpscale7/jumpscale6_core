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
from .PythonPackage import PythonPackage


j.base.loader.makeAvailable(j, 'packages')

j.packages.jumpscale=JPackageClient()
j.packages.jumpscale.releaseMgmt=ReleaseMgmt()
j.packages.jumpscale.metadataScanner=JPackageMetadataScanner()

j.packages.ijumpscale=JPackageIClient()

platformid = None
try:
    import lsb_release
    platformid = lsb_release.get_distro_information()['ID']
except ImportError:
    exitcode, platformid = j.system.process.execute('lsb_release -i -s', False)
    platformid = platformid.strip()

if platformid in ('Ubuntu', 'LinuxMint'):
    j.packages.native = j.system.platform.ubuntu

j.packages.python = PythonPackage()
