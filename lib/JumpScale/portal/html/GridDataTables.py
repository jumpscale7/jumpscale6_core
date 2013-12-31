from JumpScale import j

class GridDataTables:

    def __init__(self, page, online=False):
        self.page = page
        if online:
            self.liblocation = "https://bitbucket.org/incubaid/jumpscale-core-6.0/raw/default/extensions/html/htmllib"
        else:
            # extpath=inspect.getfile(self.__init__)
            # extpath=j.system.fs.getDirName(extpath)
            self.liblocation = "/lib"

        self.page.addJS("%s/datatables/jquery.dataTables.min.js" % self.liblocation)
        self.page.addBootstrap()

    def addTableFromActorModel(self, appname, actorname, modelname, fields, fieldids, fieldnames):
        key = j.apps.system.contentmanager.extensions.datatables.storInCache(appname, actorname, modelname, fields, fieldids, fieldnames)
        url = "/restmachine/system/contentmanager/modelobjectlist?appname=%s&actorname=%s&modelname=%s&key=%s" % (appname, actorname, modelname, key)
        self.addTableFromURL(url, fieldnames)
        return self.page

    def addTableFromURL(self, url, fieldnames):
        import random
        tableid = 'table%s' % random.randint(0, 1000)

        self.page.addCSS("%s/datatables/DT_bootstrap.css" % self.liblocation)
        # self.page.addJS("%s/datatables/DT_bootstrap.js"% self.liblocation)
        self.page.addJS("%s/datatables/dataTables.bootstrap.js" % self.liblocation)
        # self.page.addCSS("%s/datatables/demo_page.css"% self.liblocation)
        # self.page.addCSS("%s/datatables/demo_table.css"% self.liblocation)

        C = """
$(document).ready(function() {
    $('#$tableid').dataTable( {
        "sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row'<'span6'i><'span6'p>>",
        "bProcessing": false,
        "bServerSide": false,
        "sAjaxSource": "$url"
    } );
    $.extend( $.fn.dataTableExt.oStdClasses, {
        "sWrapper": "dataTables_wrapper form-inline"
    } );
} );"""
        C = C.replace("$url", url)
        C = C.replace("$tableid", tableid)
        self.page.addJS(jsContent=C, header=False)

#<table cellpadding="0" cellspacing="0" border="0" class="display" id="example">
# <table class="table table-striped table-bordered" id="example" border="0" cellpadding="0" cellspacing="0" width="100%">

        C = """
<div id="dynamic">
<table class="table table-striped table-bordered" id=$tableid border="0" cellpadding="0" cellspacing="0" width="100%">
    <thead>
        <tr>
$fields
        </tr>
    </thead>
    <tbody>
        <tr>
            <td colspan="5" class="dataTables_empty">Loading data from server</td>
        </tr>
    </tbody>
</table>
</div>"""

        fieldstext = ""
        for name in fieldnames:
            fieldstext += "<th>%s</th>\n" % (name)
        C = C.replace("$fields", fieldstext)
        C = C.replace("$tableid", tableid)

        self.page.addMessage(C, isElement=True, newline=True)
        return self.page

    def prepare4DataTables(self):
        self.page.addCSS("%s/datatables/DT_bootstrap.css" % self.liblocation)
        self.page.addJS("%s/datatables/DT_bootstrap.js"% self.liblocation)
        C = """
         $(document).ready(function() {
         $('.dataTable').dataTable( {
                "sDom": "<'row'<'span6'l><'span6'f>r>t<'row'<'span6'i><'span6'p>>",
                "sPaginationType": "bootstrap",
                "bDestroy": true,
                "oLanguage": {
                        "sLengthMenu": "_MENU_ records per page"
                }
        } );
} );
"""
        self.page.addJS(jsContent=C, header=False)
        self.page.functionsAdded["datatables"] = True
        return self.page
