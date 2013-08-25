from JumpScale import j
from .OSISFactory import OSISFactory
import JumpScale.baselib.hrd
import JumpScale.baselib.key_value_store
j.base.loader.makeAvailable(j, 'core')
j.core.osis = OSISFactory()
