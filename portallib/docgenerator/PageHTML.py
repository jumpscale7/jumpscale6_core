
from OpenWizzy import o
from Page import Page
import copy
import json

class PageHTML(Page):
    """
    the methods add code to the self.body part !!!!!
    """
    def __init__(self,name,content="",htmllibPath=None,online=False,stylesheet=None):
        """
        @param stylesheet if 'local' will get stylesheet from disk, otherwise can specify other stylesheet
        """
        Page.__init__(self,name,content)

        #self.title = "<title>%s</title>\n" % name
        self.title = ""
        self.head = ""
        self.libs = ""
        #self.body = "<div class='heading'><h1>%s</h1></div>\n" % name
        self.body = ""
        self.projectname=""
        self.logo=""
        self.scriptBody = ""
        self.jscsslinks={}
        self.login=False
        self.divlevel=[]
        self._inBlock=False
        self._inBlockType=""
        self._inBlockClosingStatement=""
        self._bulletslevel=0
        self._codeblockid=0
        self._hasmenu=False
        self._hostbasedmacro = False
        self.hasfindmenu=False
        self.padding=True
        self.pagemirror4jscss=None
        self.processparameters = {} 
        

        if htmllibPath<>None:
            self.liblocation=htmllibPath
        else:
            if online:
                self.liblocation="https://bitbucket.org/incubaid/openwizzy-core-6.0/raw/default/extensions/core/docgenerator/htmllib"
            else:
                self.liblocation=o.system.fs.joinPaths(o.tools.docgenerator.pm_extensionpath,"htmllib")

        self._hasCharts = False
        self._hasCodeblock = False
        self._hasBootstrap=False
        self._hasSidebar=False
        self.functionsAdded={}
        self._explorerInstance=0
        self._lineId=0
        self.documentReadyFunctions=[]

        chartTemplatePath = o.system.fs.joinPaths(o.system.fs.getDirName(__file__),"templates", "chart.js")
        self._chartTemplateContent = o.system.fs.fileGetContents(chartTemplatePath)
        self._chartId = 44

        #pieTemplatePath = o.system.fs.joinPaths(o.system.fs.getDirName(__file__),"templates", "pie.js")
        #self._pieTemplateContent = o.system.fs.fileGetContents(pieTemplatePath)    
        #self._pieId = 100

        #lineTemplatePath = o.system.fs.joinPaths(o.system.fs.getDirName(__file__),"templates", "line.js")
        #self._lineTemplateContent = o.system.fs.fileGetContents(lineTemplatePath)
        #self._lineId = 150

        if stylesheet=="local":
            stylesheet = o.system.fs.joinPaths(o.system.fs.getDirName(__file__), "style.css")
            if o.system.fs.exists(stylesheet):
                css=o.system.fs.fileGetContents(stylesheet)
                self.addCSS("", css)

    def addMessage(self, message, newline=False, isElement=True,blockcheck=True):
        if blockcheck:
            #print "blockcheck %s" % message
            self._checkBlock("","","")
        #else:
            #print "no blockcheck %s" % message
        message=str(message)
        message=message.replace("text:u","")
        message.strip("'")
        message=message.strip()
        message=message.replace("\r","")
        if message != '' and isElement:
            message = "%s" % message
        elif newline and message != '':
            message = "<p>%s</p><br/>" % message
        elif newline and message == '':
            message = '<br/>'
        elif message=="":
            pass
        else:
            message = "<p>%s</p>" % message

        if message != "":
            self.body="%s%s\n" % (self.body,message)

    def addParagraph(self,message):
        self.addMessage(message,isElement=False)

    def addBullet(self,message,level=1, bullet_type='bullet', tag='ul', attributes=''):
        self._checkBlock(bullet_type,"","</{0}>".format(tag))
        if level > self._bulletslevel:
            for i in range(level - self._bulletslevel):
                self.addMessage("<{0} {1}>".format(tag, attributes), blockcheck=False)
            self._bulletslevel = level
        if level < self._bulletslevel:
            for i in range(self._bulletslevel - level):
                self.addMessage("</{0}>".format(tag), blockcheck=False)
            self._bulletslevel = level
        self.addMessage("<li>%s</li>" % message, blockcheck=False)

    def _checkBlock(self,ttype,open,close):
        """
        types are : bullet,descr
        """
        #print "checkblock inblock:%s ttype:%s intype:%s" %(self._inBlock,ttype,self._inBlockType)
        if self._inBlock:
            if self._inBlockType<>ttype:
                if self._inBlockType in ("bullet", "number"):
                    for i in range(self._bulletslevel):
                        self.addMessage(self._inBlockClosingStatement,blockcheck=False)
                    self._bulletslevel=0
                else:
                    self.addMessage(self._inBlockClosingStatement,blockcheck=False)
                if open<>"":
                    self.addMessage(open,blockcheck=False)
                    self._inBlock=True
                    self._inBlockType=ttype
                    self._inBlockClosingStatement=close
                else:
                    self._inBlock=False
                    self._inBlockType=""
                    self._inBlockClosingStatement=""
        else:
            self.addMessage(open,blockcheck=False)
            if ttype<>"" and close<>"":
                self._inBlock=True
                self._inBlockType=ttype
                self._inBlockClosingStatement=close
        #print "checkblock END: inblock:%s ttype:%s intype:%s" %(self._inBlock,ttype,self._inBlockType)


    def addDescr(self,name,descr):
        self._checkBlock("descr","<dl class=\"dl-horizontal\">","</dl>")
        self.addMessage("<dt>%s</dt>\n<dd>%s</dd>" % (name,descr),blockcheck=False)

    def addBullets(self,messages,level=1):
        """
        messages: list of bullets
        """

        #todo: figure a way for nested bullets!!
        bullets = '<ul>'
        for message in messages:
            bullets += '<li>%s</li>' % message
        bullets += '</ul>';
        self.addMessage(bullets,blockcheck=False)

    def addNewLine(self, nrlines=1):
        for line in range(nrlines):
            self.addMessage("", True, isElement=True)

    def addHeading(self,message,level=1):
        message=str(message)
        heading = "<h%s>%s</h%s>" % (level, message, level)
        self.addMessage(heading, isElement=True)

    def addList(self,rows,headers="",showcolumns=[],columnAliases={},classparams="table-condensed table-hover",linkcolumns=[]):
        """
        @param rows [[col1,col2, ...]]  (array of array of column values)
        @param headers [header1, header2, ...]
        @param linkcolumns has pos (starting 0) of columns which should be formatted as links  (in that column format needs to be $description__$link
        """
        if self.functionsAdded.has_key("datatables"):
            classparams+=" display dataTable"
        if len(rows)==0:
            return False
        l=len(rows[0])
        if str(headers) != "" and headers<>None:
            if l != len(headers):
                headers=[""]+headers
            if l != len(headers):
                #raise RuntimeError("Cannot process headers, wrong nr of cols")
                from OpenWizzy.core.Shell import ipshellDebug,ipshell
                print "DEBUG NOW Cannot process headers, wrong nr of cols"
                ipshell()

                print "Cannot process headers, wrong nr of cols"
                self.addMessage("ERROR header wrong nr of cols:%s" % headers)
                headers=[]

            #if len(headers) > l:
                #while len(headers) != l:
                    #headers.pop(0)

        ##@todo does not work
        #if showcolumns != []:
            #rows2=rows
            #rows=[]
            #for row in rows2:
                #if row[0] in showcolumns:
                    #rows.append(row)
            #headers.insert(0," ")

        c="<table  class='table %s'>\n"%classparams  #the content
        if headers != "":
            c+="<thead><tr>\n"
            for item in headers:
                if item=="":
                    item=" "
                c = "%s<th>%s</th>\n" % (c,item)
            c += "</tr></thead>\n"
        rows3=copy.deepcopy(rows)
        c += "<tbody>\n"
        for row in rows3:
            c += "<tr>\n"
            if columnAliases.has_key(row[0]):
                row[0]=columnAliases[row[0]]
            colnr=0
            for col in row:
                if col=="":
                    col=" "
                if colnr in linkcolumns:
                    if len(col.split("__"))<>2:
                        raise RuntimeError("column which represents a link needs to be of format $descr__$link, here was:%s" % col)
                    c += "<td>%s</td>\n" % self.getLink(col.split("__")[0],col.split("__")[1])
                else:
                    c += "<td>%s</td>\n" % self.getRound(col)
                colnr+=1
            c += "</tr>\n"
        c += "</tbody></table>\n\n"
        self.addMessage(c,True, isElement=True)

    def addDict(self,dictobject,description="",keystoshow=[],aliases={},roundingDigits=None):
        """
        @params aliases is dict with mapping between name in dict and name to use
        """
        if keystoshow==[]:
            keystoshow=dictobject.keys()
        self.addMessage(description)
        arr=[]
        for item in keystoshow:
            if aliases.has_key(item):
                name=aliases[item]
            else:
                name=item
            arr.append([name,dictobject[item]])
        self.addList(arr)
        self.addNewLine()

    def getLink(self, description, link, link_id=None, link_class=None):
        if link_id:
            link_id = ' id="%s"' % link_id.strip()
        else:
            link_id = ''

        if link_class:
            link_class = ' class="%s"' % link_class.strip()
        else:
            link_class = ''

        anchor = "<a href='%s' %s %s>%s</a>" % (link.strip(), link_id.strip(), link_class, description)
        return anchor

    def addLink(self, description, link):
        anchor = self.getLink(description, link)
        self.addParagraph(anchor)

    def addPageBreak(self,):
        self.addMessage("<hr style='page-break-after: always;'/>")

    def addActionBox(self,actions):
        """
        @actions is array of array, [[$actionname1,$params1],[$actionname2,$params2]]
        """
        row=[]
        for item in actions:
            action=item[0]
            actiondescr=item[1]
            if actiondescr=="":
                actiondescr=action
            params=item[2]

            if self.actions.has_key(action):
                link=self.actions[action]
                link=link.replace("{params}",params)
                row.append(self.getLink(actiondescr,link))
            else:
                raise RuntimeError("Could not find action %s"%action)
        self.addList([row])

    def addCodeBlock(self,code,template="python",path="",edit=False,exitpage=True, spacename='', pagename=''):
        """
        @todo define types of templates supported
        @template e.g. python
        if path is given and edit=True then file can be editted and a edit button will appear on editor             
        """
        #if codeblock no postprocessing(e.g replacing $$space, ...) should be
        #done
        if edit:
            self.processparameters['postprocess'] = False
        self.addJS("%s/codemirror/lib/codemirror.js"% self.liblocation)
        self.addCSS("%s/codemirror/lib/codemirror.css"% self.liblocation)
        self.addJS("%s/codemirror/mode/javascript/javascript.js"% self.liblocation)
        self.addCSS("%s/codemirror/theme/elegant.css"% self.liblocation)
        #self.addCSS("%s/codemirror/doc/docs.css"% self.liblocation)
        self.addJS("%s/codemirror/mode/%s/%s.js" % ( self.liblocation,template,template))
        CSS="""
<style type="text/css">
      .CodeMirror {border-top: 1px solid black; border-bottom: 1px solid black}
      .CodeMirror-scroll { height: 100% }
</style>
"""
        self.head+=CSS
        self._codeblockid+=1
        TA="<textarea id=\"code%s\" name=\"code%s\" rows=\"5\">" % (self._codeblockid,self._codeblockid)
        TA+=code
        TA+="</textarea>"
        if path<>"" and edit:
            TA+="<button type=\"submit\" onclick=\"copyText%s();\">Save.</button>"%self._codeblockid
        self.addMessage(TA)
    
        if path<>"" and edit:

            F="""
    <form id="hiddenForm$id" name="hiddenForm$id" method="post" action="/restmachine/system/contentmanager/wikisave">
    <input type="hidden" name="text" id="text" value="">
    <input type="hidden" name="cachekey" id="cachekey" value="$guid">
    </form>
            """
            F=F.replace("$id",str(self._codeblockid))
            guid=o.base.idgenerator.generateGUID()
            content = {'space': spacename, 'path': path, 'page': pagename}
            o.apps.system.contentmanager.dbmem.cacheSet(guid,content,60)
            F=F.replace("$guid",guid)
            self.addMessage(F)

        #if not self._hasCodeblock:
        JS="""
var editor$id = CodeMirror.fromTextArea(document.getElementById("code$id"),
    {
    lineNumbers: true,
    theme: "elegant",
    mode: "{template}",
    onCursorActivity: function() {
        editor$id.setLineClass(hlLine, null, null);
        hlLine = editor$id.setLineClass(editor$id.getCursor().line, null, "activeline");
        }
    }
);
var hlLine = editor$id.setLineClass(0, "activeline");

function copyText$id() {
    var text=editor$id.getValue()
    document.hiddenForm$id.text.value = text;
    document.forms["hiddenForm$id"].submit();
    }
"""
       
        JS=JS.replace("$id",str(self._codeblockid))
        self.addJS(jsContent=JS.replace("{template}",template),header=False)
        self._hasCodeblock=True



    def addCodePythonBlock(self,code,title="",removeLeadingTab=True):
        #todo
        if removeLeadingTab:
            check=True
            for line in code.split("\n"):
                if not(line.find("    ")==0 or line.strip()==""):
                    check=False
            if check==True:
                code2=code
                code=""
                for line in code2.split("\n"):
                    code+="%s\n"%line[4:]
        self.addCodeBlock(code)


    def addLineChart(self, title, rows, headers="", width=800, height=400):
        """
        @param rows [[values, ...],]  first value of the row is the rowname e.g. cost, revenue
        @param headers [] first value is name of the different rowtypes e.g. P&L
        """

        legend = list()

        headers2=[]
        prev=""
        for item in headers:
            if item<>prev:
                headers2.append(item)
                prev=item
            else:
                headers2.append("")

        if len(rows)==0:
            return False
        data = ""
        for row in rows:
            data += str(row[1:]) + ","
            legend.append(row[0])

        data = data[:-1]

        self._addChartJS()
        self._lineId += 1
        lineId = 'line-%s' % (self._lineId)

        if headers == "":
            headers = []

        te=o.codetools.templateengine.new()
        te.add('lineId',lineId)
        te.add('lineTitle',title)
        te.add('lineData',data)
        te.add('lineHeaders',str(headers2))
        te.add('lineLegend',str(legend))
        te.add('lineWidth',str(width))
        te.add('lineHeight',str(height))

        C="""
    var line = new RGraph.Line("{lineId}", {lineData});
    
    line.Set('chart.title', '{lineTitle}');
    line.Set('chart.linewidth', 1);
    line.Set('chart.labels', {lineHeaders});
    line.Set('chart.key', {lineLegend});
    line.Set('chart.gutter.left', 90);
    RGraph.Effects.Line.jQuery.Trace(line);
    
    line.Draw();        
        """

        jsContent = te.replace(C)        
        lineContainer = "<canvas id='%s' width='%s' height='%s' >[No Canvas Support!]</canvas>" % (lineId, width, height)
        self.addMessage(lineContainer, isElement=True, newline=True)

        self.addJS(jsContent=jsContent,header=False)


    def addBarChart(self, title, rows, headers="", width=900, height=400, showcolumns=[], columnAliases={}, onclickfunction=''):
        """
        order is list of items in rows & headers, defines the order and which columns to show
        """
        data = list()
        legend = list()
        newRows = []
        for row in rows:
            newRow = [row[0]] + [int(n) for n in row[1:]]
            newRows.append(newRow)
        rows = newRows

        if len(rows)==0:
            return False

        if showcolumns != []:
            rows2=rows
            rows=[]
            for row in rows2:
                if row[0] in showcolumns:
                    rows.append(row)

        data = [list(x) for x in zip(*rows)][1:]

        for row in rows:
            if columnAliases.has_key(row[0]):
                legend.append(columnAliases[row[0]])
            else:
                legend.append(row[0])

        if str(headers) != "":
            if len(headers) == len(data)+1:
                headers=headers[1:]
            #headers=[""]+headers
            if len(headers) != len(data):
                #raise RuntimeError("headers has more items then nr columns")
                print "Cannot process headers, wrong nr of cols"
                self.addMessage("ERROR header wrong nr of cols:%s" % headers)
                headers=[]


                #headers = [] #Wrong number of headers
        else:
            headers = []

        self._addChartJS()
        self._chartId += 1
        chartId = 'chart-%s' % (self._chartId)

        te=o.codetools.templateengine.new()
        te.add('chartId',chartId)
        te.add('chartTitle',title)
        te.add('chartData',str(data))
        te.add('chartHeaders',str(headers)) #labels
        te.add('chartLegend',str(legend))
        te.add('chartWidth',str(width))
        te.add('chartHeight',str(height))
        if onclickfunction == '':
            onclickfunction = 'function(){}'
        te.add('onclickfunction', onclickfunction)
        
        jsContent = te.replace(self._chartTemplateContent)

        self.addScriptBodyJS(jsContent)
        chartContainer = "<canvas id='%s' width='%s' height='%s' >[No Canvas Support!]</canvas>" % (chartId, width, height)
        self.addMessage(chartContainer, isElement=True, newline=True)

    def addPieChart(self, title, data, legend, width=1000, height=600):
        """
        Add pie chart as the HTML element
        @param data is array of data points
        @param legend [legendDataPoint1, legendDataPoint2, ..]
        """
        self._addChartJS()
        self._pieId += 1
        pieId = 'pie-%s' % (self._pieId)

        te=o.codetools.templateengine.new()
        te.add('pieId',pieId)
        te.add('pieTitle',title)
        te.add('pieData',str(data))
        te.add('pieLegend', str(legend))

        jsContent = te.replace(self._pieTemplateContent)

        self.addScriptBodyJS(jsContent)
        pieContainer = "<canvas id='%s' width='%s' height='%s' >[No Canvas Support!]</canvas>" % (pieId, width, height)
        self.addMessage(pieContainer, isElement=True, newline=True)

    @staticmethod
    def _format_styles(styles):
        """
        Return CSS styles, given a list of CSS attributes
        @param styles a list of tuples, of CSS attributes, e.g. [("background-color", "green), ("border", "1px solid green")]

        >>> PageHTML._format_styles([("background-color", "green"), ("border", "1px solid green")])
        'background-color: green; border: 1px solid green'
        """
        try:
            return '; '.join('{0}: {1}'.format(*style) for style in styles)
        except IndexError:
            return ''

    def addImage(self, title, imagePath, width=None, height=None, styles=[]):
        """
        @param title alt text of the image
        @param imagePath can be url or local path
        @param width width of the image
        @param height height of the image
        @param styles a list of tuples, containing CSS attributes for the image, e.g. [("background-color", "green), ("border", "1px solid green")]
        """
        width_n_height = ''
        if width:
            width_n_height += ' width="{0}"'.format(width)
        if height:
            width_n_height += ' height="{0}"'.format(height)

        img = "<img src='%s' alt='%s' %s style='clear:both;%s' />" % (imagePath, title, width_n_height, PageHTML._format_styles(styles))
        self.addMessage(img, isElement=True)

    def addTableWithContent(self,columnsWidth,colContents):
        """
        @param columnsWidth = Array with each element a nr, when None then HTML does the formatting, otherwise relative to each other
        @param colContents = array with each element HTML code
        """
        table = "<table><thead><tr>"
        for colWidth, colContent in zip(columnsWidth, colContents):
            if colWidth:
                table += "<th width='%s'>%s</th>" % (colWidth, colContent)
            else:
                table += "<th>%s</th>" % (colContent)
        table += "</tr></head></table>"
        self.addMessage(table, isElement=True)

    def addHTML(self,htmlcode):
        #import cgi
        #html = "<pre>%s</pre>" % cgi.escape(htmlcode)
        self.addMessage(htmlcode, isElement=False)

    def removeCSS(self, exclude,permanent=False):
        """
        will walk over header and remove css links
        link need to be full e.g. bootstrap.min.css
        """
        out=""
        for line in self.head.split("\n"):
            if line.lower().find(exclude)==-1:
                out+="%s\n"%line
        self.head=out
        if permanent:
            key=exclude.strip().lower()
            self.jscsslinks[key]=True
        


    def addCSS(self, cssLink=None, cssContent=None,exlcude=""):
        """
        """
        if self.pagemirror4jscss<>None:
            self.pagemirror4jscss.addCSS(cssLink, cssContent)
        if cssLink<>None:
            key=cssLink.strip().lower()
            if self.jscsslinks.has_key(key):
                return
            self.jscsslinks[key]=True

        if cssContent:
            css = "<style type='text/css'>\n%s</style>\n" % cssContent
        else:
            css = "<link  href='%s' type='text/css' rel='Stylesheet'/>\n" % cssLink
        self.head += css

    def addJS(self, jsLink=None, jsContent=None,header=True):
        if self.pagemirror4jscss<>None:
            self.pagemirror4jscss.addJS(jsLink, jsContent,header)        
        if jsLink<>None:
            key=jsLink.strip().lower()
            if self.jscsslinks.has_key(key):
                return
            self.jscsslinks[key]=True

        if jsContent:
            js = "<script type='text/javascript'>\n%s</script>\n" % jsContent
        else:
            js = "<script  src='%s' type='text/javascript'></script>\n" % jsLink
            #js = "<script  src='%s' </script>\n" % jsLink
        if header:
            self.head += js
        else:
            self.body +=js

    def addScriptBodyJS(self, jsContent):
        self.scriptBody = "%s%s\n" % (self.scriptBody, jsContent)

    def _addChartJS(self):
        if self._hasCharts:
            return

        self.addJS("%s/rgraph/RGraph.common.core.js" % self.liblocation)
        self.addJS("%s/rgraph/RGraph.bar.js" % self.liblocation)
        self.addJS("%s/rgraph/RGraph.pie.js" % self.liblocation)
        self.addJS("%s/rgraph/RGraph.line.js" % self.liblocation)
        self.addJS("%s/rgraph/RGraph.common.key.js"  % self.liblocation)
        self.addJS("%s/rgraph/RGraph.common.effects.js"  % self.liblocation)
        self.addJS("%s/rgraph/RGraph.common.dynamic.js"  % self.liblocation)

        self._hasCharts = True

    def addBootstrap(self,jquery=True):
        if self._hasBootstrap:
            return
        self._hasBootstrap=True
        if jquery:
            self.addJS("%s/jquery-latest.js"  % self.liblocation)
        self.addJS("%s/bootstrap/js/bootstrap.js"  % self.liblocation)
        self.addJS("%s/jquery.cookie.js"  % self.liblocation)
        #self.addCSS("%s/bootstrap/css/bootstrap.min.css"% self.liblocation)
        self.addCSS("%s/bootstrap/css/bootstrap.css"% self.liblocation)
        self.addCSS("%s/bootstrap/css/bootstrap-responsive.css"% self.liblocation)

    def addHostBasedContent(self):
        if self._hostbasedmacro:
            return
        else:
            extracontent = """
    filter_div = function(par) {
         host = window.location.hostname
         if (host == par['hostname'])
         {
              doc = document.getElementById(par['divid'])
              if (doc != null)
              {
                doc.style.visibility = "visible";
                doc.style.display = "inline";
              }
         }
    }
    $(document).ready(function() { tocheck.map(filter_div);})
    """  
            self.addJS(jsContent=extracontent)
            self._hostbasedmacro = True

    def addDocumentReadyJSfunction(self,function):
        """
        e.g. $('.dataTable').dataTable();
        """
        if self.pagemirror4jscss<>None:
            self.pagemirror4jscss.addDocumentReadyJSfunction(function) 
        self.documentReadyFunctions.append(function)


    def addExplorer(self,path="",dockey=None,height=500,width=750,readonly=False,tree=False):

        self.addJS("%s/lib/elfinder/jquery.min.js"  % self.liblocation)
        self.addJS("%s/lib/elfinder/jquery-ui.min.js"  % self.liblocation)
        self.addCSS("%s/lib/elfinder/jquery-ui.css"  % self.liblocation)
        self.addCSS("%s/elfinder/css/elfinder.min.css"% self.liblocation)
        self.addCSS("%s/elfinder/css/theme.css"% self.liblocation)
        self.addJS("%s/elfinder/js/elfinder.min.js"  % self.liblocation)

        def writeExplorerPHP(path,dockey):
            path=o.system.fs.pathNormalize(path).replace("\\","/")
            path2=o.system.fs.joinPaths(o.system.fs.getcwd(),"libphp","elfinder","connector.php").replace("\\","/")
            C=o.system.fs.fileGetContents(path2)
            if o.system.platformtype.isWindows():
                root='c:/qb6/apps/ishare/'
            else:
                root="/opt/qbase6/apps/ishare/"
            C=C.replace("{path}",path)
            C=C.replace("{root}",root)
            
            dest= o.system.fs.joinPaths(o.core.portal.runningPortal.webserver.filesroot,dockey).replace("\\","/")

            if not o.system.fs.exists(dest):
                if o.system.fs.isLink(dest):
                    o.system.fs.unlink(dest)
                o.system.fs.symlink(path,dest)
            C=C.replace("{rootdownload}","/%s"%dockey)
            pathout=o.system.fs.joinPaths(o.system.fs.getcwd(),"libphp","elfinder","connector_%s.php"%dockey).replace("\\","/")
            o.system.fs.writeFile(pathout,C) #@todo need to do something here as well to have readonly behaviour
            return "connector_%s.php"%dockey

        if readonly:
            commands="""
	    commands : [
	    'open', 'reload', 'home', 'up', 'back', 'forward', 'getfile',
	    'download', 'archive',
	    'resize', 'sort'
	    ],"""

            dircmd="'reload', 'back'"
            filecmd="'open', '|', 'download', '|', 'archive',"
        else:
            #customData : {rootpath:'$path'} ,
            commands="""
	    commands : [
	    'open', 'reload', 'home', 'up', 'back', 'forward', 'getfile',
	    'download', 'rm', 'duplicate', 'rename', 'mkdir', 'mkfile', 'upload', 'copy',
	    'cut', 'paste','extract', 'archive', 'help',
	    'resize', 'sort'
	    ],"""
            dircmd="'reload', 'back', '|', 'upload', 'mkdir', 'mkfile', 'paste'"
            filecmd="'getfile', '|','open', '|', 'download', '|', 'copy', 'cut', 'paste', 'duplicate', '|',\
	                'rm', '|', 'edit', 'rename', 'resize', '|', 'archive', 'extract',"

        C="""
<script type="text/javascript" charset="utf-8">
     $().ready(function() {

        var options=
        {
            defaultView : 'list',
	        url : '/elfinder/$connector',
	        height : $height,
            width : $width,
	        {commands}
	        ui :[{tree}'path', 'stat'],

	        $EDITOR
	        handlers :
            {
	            // extract archive files on upload
	            upload : function(event, instance)
	            {
	                var uploadedFiles = event.data.added;
	                var archives = ['application/zip', 'application/x-gzip', 'application/x-tar', 'application/x-bzip2'];
	                for (i in uploadedFiles)
	                {
	                    var file = uploadedFiles[i];
	                    if (jQuery.inArray(file.mime, archives) >= 0)
	                    {
                        instance.exec('extract', file.hash);
                        }
                    }
	            },
                open   : function(event) { console.log(event.data); }
	        },
	        contextmenu :
            {
	          // navbarfolder menu
	          //navbar : ['open', '|', 'copy', 'cut', 'paste', 'duplicate', '|', 'rm'],

	          // current directory menu
	          cwd    : [{dircmd}],

	          // current directory file menu
	          files  : [
	                {filecmd}
              ]
	        },
            ui: ['toolbar'],
            uiOptions :
            {
                toolbar : [
		['back', 'forward'],
        ['reload'],
        ['home', 'up']
	],
            	tree :
                {
                    // expand current root on init
                    openRootOnLoad : true,
                    // auto load current dir parents
                    //syncTree : true
                },
                // navbar options
                navbar : {
                    minWidth : 100,
                    maxWidth : 100
                },
            },
        }

        $('#elfinder{nr}').elfinder(options);
	});
</script>
"""
        #//var elf = $('#elfinder').elfinder(options);
        C=C.replace("$path",path)
        height=str(height)
        C=C.replace("$height",str(height))
        C=C.replace("$width",str(width))
        C=C.replace("$EDITOR","")
        C=C.replace("{commands}",commands)
        self._explorerInstance+=1
        C=C.replace("{nr}",str(self._explorerInstance))
        if tree:
            C=C.replace("{tree}","'places', 'tree',")
        else:
            C=C.replace("{tree}","")

        C=C.replace("{dircmd}",dircmd)
        C=C.replace("{filecmd}",filecmd)
        if dockey==None:
            dockey=o.base.byteprocessor.hashMd5(path)

        C=C.replace("$connector",writeExplorerPHP(path,"key__%s"%dockey))
        self.head+=C
        self.addBootstrap(jquery=False)
        self.addMessage("<div id=\"elfinder%s\"></div>"%self._explorerInstance)


    #def _generateFromTemplate(self, filePath, params):
        #fd = open(filePath, 'r')
        #contents = fd.read()
        #fd.close()
        #from Cheetah.Template import Template
        #template = Template(contents, params)
        #contents = str(template)
        #return contents

    #def _generateChartFromTemplate(self, params):
        #return self._generateFromTemplate(self._chartTemplate, params)

    #def _generateLineFromTemplate(self, params):
        #return self._generateFromTemplate(self._lineTemplate, params)

    #def _generatePieFromTemplate(self, params):
        #return self._generateFromTemplate(self._pieTemplate, params)

    def _generateChartScript(self):
        js = ""
        if(self._hasCharts):
            js = "<script type='text/javascript'>\n%s\n" % "window.onload = function () {"
            js += self.scriptBody
            js += "\n};\n</script>\n"
        return js

    def addHTMLHeader(self,header):
        self.head+=header

    def addHTMLBody(self,body):
        self.body+=body


    def getContent(self):
        return str(self)

    def __str__(self):
        #make sure we get closures where needed (/div)
        self._checkBlock("DDD","","")
        if self.title<>"":
            title="<title>%s</title>\n" % self.title
        else:
            title=""

        jsHead = title+self.head + self._generateChartScript()

        if (self.login or self._hasmenu) and (self.padding<>False):
            jsHead+="<style type='text/css'>\n"
            if self.padding<>True and self.padding.find("-")<>-1:
                top,bottomn=self.padding.split("-")
                top=int(top.strip())
                bottomn=int(bottomn.strip())
                jsHead+="body {padding-top: %spx; padding-bottom: %spx;}</style> \n"%(top,bottomn)
            else:
                jsHead+="body {padding-top: 60px; padding-bottom: 40px;}</style> \n"

        if self._hasSidebar:
            jsHead+="<style type='text/css'> body.sidebar-nav {padding: 9px 0;} </style> \n"

        # if self.pagemirror4jscss<>None:
        #     self.pagemirror4jscss.jsHead+=jsHead

        if self.documentReadyFunctions<>[]:
            CC="$(document).ready(function() {\n"
            for f in self.documentReadyFunctions:
                CC+="%s\n"%f
            CC+="} );\n"
            self.addJS(jsContent=CC)


        return '<!DOCTYPE html>\n<html>\n \
        <head>\n%s\n</head>\n \
        <body>\n%s</body>\n</html>' % ( jsHead, self.body)


