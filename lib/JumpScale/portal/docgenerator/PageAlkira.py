
from JumpScale import j
from page import Page
import copy


class PageAlkira(Page):  # @todo P1 adjust this code to work for Alkira (note certain items are P3)

    def __init__(self, name, content, parent="Home"):
        Page.__init__(name, content, parent)

    def addMessage(self, message, newline=False):
        message = message.strip()
        message = message.replace("\r", "")
        if newline:
            message += "\n"
        if message != "":
            self.content = "%s%s\n" % (self.content, message)

    def addBullet(self, message, level=1):
        bullets = ""
        for i in range(level):
            bullets += "*"
        message = "%s %s" % (bullets, message)
        self.addMessage(message)

    def addNewLine(self):
        self.addMessage("", True)

    def addHeading(self, message, level=1):
        message = "h%s. %s" % (level, message)
        self.addMessage(message, True)

    def addList(self, rows, headers="", showcolumns=[], columnAliases={}):
        """
        @param rows [[col1,col2, ...]]  (array of array of column values)
        @param headers [header1, header2, ...]
        """
        if len(rows) == 0:
            return False
        l = len(rows[0])
        if l != len(headers) and headers != "":
            if len(headers) > l:
                while len(headers) != l:
                    headers.pop(0)

        #@todo put more checks to check on validity  (id:29)
        if showcolumns != []:
            rows2 = rows
            rows = []
            for row in rows2:
                if row[0] in showcolumns:
                    rows.append(row)
            headers.insert(0, " ")

        c = ""  # the content
        if headers != "":
            for item in headers:
                c = "%s||%s" % (c, item)
            c += "||\n"
        rows3 = copy.deepcopy(rows)
        for row in rows3:
            if row[0] in columnAliases:
                row[0] = columnAliases[row[0]]
            for col in row:
                if col == "":
                    col = " "
                c += "|%s" % self.getRound(col)
            c += "|\n"
        self.addMessage(c, True)

    def addDict(self, dictobject, description="", keystoshow=[], aliases={}, roundingDigits=None):
        """
        @params aliases is dict with mapping between name in dict and name to use
        """
        if keystoshow == []:
            keystoshow = dictobject.keys()
        self.addMessage(description)
        arr = []
        for item in keystoshow:
            if item in aliases:
                name = aliases[item]
            else:
                name = item
            if roundingDigits == None:
                arr.append([name, dictobject[item]])
            elif roundingDigits == 0:
                arr.append([name, int(round(dictobject[item], roundingDigits))])
            else:
                arr.append([name, round(dictobject[item], roundingDigits)])
        self.addList(arr)
        self.addNewLine()

    def getLink(self, description, link):
        return "[%s|%s]" % (description, link)

    def addLink(self, description, link):
        msg = self.getLink(description, link)
        self.addBullet(msg)

    def addPageBreak(self,):
        msg = "{pagebreak}"
        self.addMessage(msg)

    def addActionBox(self, actions):
        """
        @actions is array of array, [[$actionname1,$params1],[$actionname2,$params2]]
        """
        #@todo P3
        row = []
        for item in actions:
            action = item[0]
            actiondescr = item[1]
            if actiondescr == "":
                actiondescr = action
            params = item[2]

            if action in self.actions:
                link = self.actions[action]
                link = link.replace("{params}", params)
                row.append(self.getLink(actiondescr, link))
            else:
                raise RuntimeError("Could not find action %s" % action)
        self.addList([row])

    def addCodeBlock(self, code):
        content = "{code}\n%s\n{code}\n" % code
        self.addMessage(content)

    def addCodePythonBlock(self, code, title="", removeLeadingTab=True):
        if removeLeadingTab:
            check = True
            for line in code.split("\n"):
                if not(line.find("    ") == 0 or line.strip() == ""):
                    check = False
            if check == True:
                code2 = code
                code = ""
                for line in code2.split("\n"):
                    code += "%s\n" % line[4:]

        if title != "":
            content = "{code:language=python|title=%s|theme=Eclipse}\n%s\n{code}\n" % (title, code)
        else:
            content = "{code:language=python|theme=Eclipse}\n%s\n{code}\n" % (code)
        self.addMessage(content)

    def _getArray2Wiki(self, rows, headers="", showcolumns=[], columnAliases={}):
        """
        @param rows [[rowname,col1,col2, ...]]  (array of array of column values with first item the rowname)
        @param headers [header1, header2, ...]
        """
        #@todo S4 P3 put more checks to check on validity  (id:84)
        #@todo S4 P3  remove code duplication with addList( (id:85)
        l = len(rows[0])
        if l != len(headers) and headers != "":
            if len(headers) > l:
                while len(headers) != l:
                    headers.pop(0)

        if showcolumns != []:
            rows2 = rows
            rows = []
            for row in rows2:
                if row[0] in showcolumns:
                    rows.append(row)

        c = ""  # the content
        if headers != "":
            for item in headers:
                if item == "":
                    item = " "
                c = "%s||%s" % (c, item)
            c += "||\n"
        rows3 = copy.deepcopy(rows)
        for row in rows3:
            if row[0] in columnAliases:
                row[0] = columnAliases[row[0]]
            for col in row:
                if col == "":
                    col = " "
                c += "|%s" % col
            c += "|\n"
        return c

    def addLineChart(self, title, rows, headers="", width=800, height=300):
        """
        @param rows [[values, ...],]  first value of the row is the rowname e.g. cost, revenue
        @param headers [] first value is name of the different rowtypes e.g. P&L
        """
        #@todo P3
        content =\
            """
{chart:title=%s|type=line|legend=true|width=%s|height=%s}
%s
{chart}
""" % (title, width, height, self._getArray2Wiki(rows, headers))
        self.addMessage(content, True)
        self.addNewLine()

    def addBarChart(self, title, rows, headers="", width=800, height=300, showcolumns=[], columnAliases={}):
        """
        order is list of items in rows & headers, defines the order and which columns to show
        """
        #@todo P3
        content =\
            """
{chart:title=%s|type=bar|legend=true|width=%s|height=%s}
%s
{chart}
""" % (title, width, height, self._getArray2Wiki(rows, headers, showcolumns, columnAliases))
        self.addMessage(content, True)
        self.addNewLine()

    def _getUnderlineString(self, message):
        line = ""
        for i in range(len(message)):
            line = line + "="
        return "%s\n%s" % (message, line)

    def __repr__(self):
        return self.content

    def __str__(self):
        return self.__repr__()
