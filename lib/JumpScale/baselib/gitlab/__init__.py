from JumpScale import j

from .GitlabConfigManagement import GitlabConfigManagement
from .GitlabFactory import *

j.base.loader.makeAvailable(j, 'clients')

j.clients.gitlab=GitlabFactory()
j.clients.gitlab._config=GitlabConfigManagement()
