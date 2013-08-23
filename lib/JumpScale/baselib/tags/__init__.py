from JumpScale import j
from .TagsFactory import TagsFactory
j.base.loader.makeAvailable(j, 'tags')
j.core.tags = TagsFactory()
