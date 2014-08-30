


from JumpScale import j

import JumpScale.baselib.celery

j.clients.celery.celeryStart(url="redis://localhost:7768/0",concurrency=4,actorsPath="actors")


