from OpenWizzy import o
from .TagsFactory import TagsFactory
o.base.loader.makeAvailable(o, 'tags')
o.core.tags = TagsFactory()
