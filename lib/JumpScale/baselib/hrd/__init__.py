from JumpScale import j
from .HumanReadableData import HumanReadableDataFactory
from ..tags.TagsFactory import TagsFactory
j.base.loader.makeAvailable(j, 'core')
j.core.hrd = HumanReadableDataFactory()
