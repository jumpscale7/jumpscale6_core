from OpenWizzy import o

from .Bitbucket import Bitbucket
from .BitbucketConfigManagement import BitbucketConfigManagement
from .BitbucketInterface import BitbucketInterface

o.base.loader.makeAvailable(o, 'clients')

o.clients.bitbucket=Bitbucket()
o.clients.bitbucket._config=BitbucketConfigManagement()
o.clients.bitbucketi=BitbucketInterface()
