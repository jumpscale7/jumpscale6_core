from JumpScale import j
from BootStrapForm import *
from GridDataTables import *

#from JumpScale import j


class HtmlFactory:

    def getPageModifierBootstrapForm(self, page):
        """
        """
        return BootStrapForm(page)

    def getPageModifierGridDataTables(self, page):
        """
        """
        return GridDataTables(page)

    def getPageModifierGalleria(self, page):
        """
        """
        return HTMLGalleria(page)

    def getHtmllibDir(self):
        dirname = j.system.fs.getDirName(__file__)
        return j.system.fs.joinPaths(dirname, 'htmllib')
