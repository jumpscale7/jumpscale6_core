from JumpScale import j

from .vcsfactory import VCSFactory
j.base.loader.makeAvailable(j, 'clients')
j.clients.vcs=VCSFactory()
