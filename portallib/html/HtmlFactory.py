from OpenWizzy import o
from BootStrapForm import *
from GridDataTables import *

#from OpenWizzy import o

class HtmlFactory:
    def getPageModifierBootstrapForm(self,page):
        """
        """
        return BootStrapForm(page)

    def getPageModifierGridDataTables(self,page):
        """
        """
        return GridDataTables(page)

    def getPageModifierGalleria(self,page):
        """
        """
        return HTMLGalleria(page)

    def getHtmllibDir(self):
        dirname = o.system.fs.getDirName(__file__)
        return o.system.fs.joinPaths(dirname, 'htmllib')
