from JumpScale import j
from .HtmlFactory import HtmlFactory
j.base.loader.makeAvailable(j, '')
j.html = HtmlFactory()
