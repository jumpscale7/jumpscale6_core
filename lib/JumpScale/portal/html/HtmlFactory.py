from JumpScale import j
from BootStrapForm import *
from GridDataTables import *

from xml.sax.saxutils import escape, unescape
# escape() and unescape() takes care of &, < and >.
html_escape_table = {
    '"': "&quot;",
    "'": "&apos;",
}

for c in "[]{}":
    html_escape_table[c] = "&#%s;" % ord(c)

html_unescape_table = {v:k for k, v in html_escape_table.items()}


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

    def escape(self, text):
        return escape(text, html_escape_table)

    def unescape(self, text):
        return unescape(text, html_unescape_table)
