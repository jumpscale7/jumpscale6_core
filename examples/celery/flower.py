
from JumpScale import j

import JumpScale.baselib.celery

j.clients.celery.flowerStart(url="redis://localhost:7768/0")
