from JumpScale import j
from GitFactory import GitFactory

j.base.loader.makeAvailable(j, 'clients')
j.clients.git = GitFactory()

try:
    import mercurial
except ImportError:
    j.system.platform.ubuntu.checkInstall("mercurial","hg")
