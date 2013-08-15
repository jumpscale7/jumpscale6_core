from OpenWizzy import o
from .HtmlFactory import HtmlFactory
o.base.loader.makeAvailable(o, '')
o.html = HtmlFactory()
