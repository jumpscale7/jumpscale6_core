from OpenWizzy import o

from .CloudSystemFS import CloudSystemFS

o.base.loader.makeAvailable(o, 'cloud.system')

o.cloud.system.fs=CloudSystemFS()

