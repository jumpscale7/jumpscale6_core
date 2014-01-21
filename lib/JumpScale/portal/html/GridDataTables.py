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

    def addTableForModel(self, namespace, category, fieldids, fieldnames=None, fieldvalues=None, filters=None):
        """
        @param namespace: namespace of the model
        @param cateogry: cateogry of the model
        @param fieldids: list of str pointing to the fields of the dataset
        @param fieldnames: list of str showed in the table header if ommited fieldids will be used
        @param fieldvalues: list of items resprenting the value of the data can be a callback
        """
        key = j.apps.system.contentmanager.extensions.datatables.storInCache(fieldids, fieldnames, fieldvalues, filters)
        url = "/restmachine/system/contentmanager/modelobjectlist?namespace=%s&category=%s&key=%s" % (namespace, category, key)
        if not fieldnames:
            fieldnames = fieldids
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
        "bProcessing": true,
        "bServerSide": true,
        "bDestroy": true,
        "sPaginationType": "bootstrap",
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
<table class="table table-striped table-bordered" id="$tableid" border="0" cellpadding="0" cellspacing="0" width="100%">
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

    def addSearchOptions(self, tableid=".dataTable"):
        self.page.addJS(jsContent='''
          $(function() {
              $('%s').each(function() {
                  var table = $(this);
                  var numOfColumns = table.find('th').length;
                  var tfoot = $('<tfoot />');
                  for (var i = 0; i < numOfColumns; i++) {
                      var td = $('<td />');
                      td.append(
                          $('<input />', {type: 'text', 'class': 'datatables_filter'}).keyup(function() {
                              table.dataTable().fnFilter(this.value, tfoot.find('input').index(this));
                          })
                      );
                      tfoot.append(td);
                  }
                  if (table.find('tfoot').length == 0)
                    table.append(tfoot);
              });
            });''' % tableid
        , header=False)

    def prepare4DataTables(self):
        self.page.addCSS("%s/datatables/DT_bootstrap.css" % self.liblocation)
        self.page.addJS("%s/datatables/DT_bootstrap.js"% self.liblocation)
        C = """
         $(document).ready(function() {
         $('.JSdataTable').dataTable( {
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
