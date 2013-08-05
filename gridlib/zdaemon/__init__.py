from OpenWizzy import o

import OpenWizzy.grid.gevent
import OpenWizzy.baselib.key_value_store
import OpenWizzy.baselib.serializers

from .ZDaemonFactory import ZDaemonFactory

o.base.loader.makeAvailable(o, 'core')
o.core.zdaemon = ZDaemonFactory()
