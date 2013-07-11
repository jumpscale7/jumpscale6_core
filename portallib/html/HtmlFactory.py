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

