from JumpScale import j
from .HumanReadableData import HumanReadableDataFactory
j.base.loader.makeAvailable(j, 'core')
j.core.hrd = HumanReadableDataFactory()
