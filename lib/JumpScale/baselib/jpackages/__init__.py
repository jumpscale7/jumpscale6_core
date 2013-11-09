from JumpScale import j
import JumpScale.baselib.actions
import JumpScale.baselib.bitbucket
import JumpScale.baselib.mercurial
import JumpScale.baselib.taskletengine
import JumpScale.baselib.blobstor
import JumpScale.baselib.cloudsystemfs


from .JPackageClient import JPackageClient
from .ReleaseMgmt import ReleaseMgmt
from .PythonPackage import PythonPackage
from .JPackagesGenDocs import JPackagesGenDocs

j.base.loader.makeAvailable(j, 'packages')

j.packages=JPackageClient()
j.packages.releaseMgmt=ReleaseMgmt()
j.packages.docGenerator=JPackagesGenDocs()

j.system.platform.python = PythonPackage()
