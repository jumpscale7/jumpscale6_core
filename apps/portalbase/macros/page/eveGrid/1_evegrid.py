
def main(j, args, params, tags, tasklet):
	page = args.page
	page.addCSS('/jslib/bootstrap/css/bootstrap.css')
	page.addCSS('/jslib/jquery/jqueryDataTable/css/dataTables.bootstrap.css')
	page.addCSS('/jslib/jquery/jqueryDataTable/css/bootstrap-theme.min.css')
	
	page.addCSS(cssContent=''' 
		.center{
            text-align: center !important;
        }
        table.dataTable tbody tr.selected td{
            background-color: #b0bed9;
        }
        .dataTables_filter, .dataTables_info { 
            display: none; 
        }
        input.searchInput{
	        height: 35px;
			line-height: 35px;
        }
	 ''')
	hrd = j.core.hrd.getHRD(content=args.cmdstr)
	eveGrid = {}
	eveGrid['schemaURL'] = getattr(hrd, 'schema_url', '')
	eveGrid['specJsonPath'] = getattr(hrd, 'spec_json_path', '')
	eveGrid['entityName'] = getattr(hrd, 'entity_name', '')


	page.addMessage('''
		<div class="container" ng-app="eveApp" ng-controller="EveController">
	        <table id="example" class="table table-striped" cellspacing="0" width="100%">
	        <tfoot>
	            <tr>
	              <td>
	                <button id="delete" class="btn btn-primary">Delete</button>
	              </td>
	            </tr>
	        </tfoot>
	        </table>
    	</div>
	 ''')

    # <form role="form" ng-show="currentItem" method="post" action="{[ '/people/' + currentItem._id ]}">
    #     <input type="hidden" id="_id" value="{[ currentItem._id ]}">
    #     <input type="hidden" id="_etag" value="{[ currentItem._etag ]}">
    #     <div class="form-group" ng-repeat="col in columns" ng-show="col.data">
    #         <label>{[ col.data ]}</label>
    #         <input type="text" factory="{[ col.factory ]}" class="form-control" id="{[ col.data ]}" ng-model="currentItem[col.data]">
    #     </div>
    #     <button type="submit" class="btn btn-default">Submit</button>
    # </form>
	page.addJS('/jslib/jquery/jqueryDataTable/js/jquery.dataTables.js')
	page.addJS('/jslib/angular/angular1-3-0.min.js')
	page.addJS('/jslib/bootstrap/js/bootstrap.min.js')
	page.addJS('/jslib/underscore/underscore-min.js')
	page.addJS('/jslib/jquery/jqueryDataTable/js/dataTables.bootstrap.js')
	
	import jinja2
	jinja = jinja2.Environment(variable_start_string="${", variable_end_string="}")

	template = jinja.from_string('''
		var eveApp = angular.module('eveApp', []);
	    eveApp.controller('EveController', function($scope, $http) {
	        $http({
            url: 'http://${schemaURL}${specJsonPath}',
             method: 'GET',

             }).then(function(data) {
	            $scope.schema = data.data;
	            $scope.columns = [{data: null, orderable: false, defaultContent: '<input class="rowCheck" type="checkbox"></input>', 'title': '<input id="allCheck" type="checkbox"></input>'}]
	                .concat($scope.schema.domains.${entityName}['/${entityName}'].POST.params
	                    .filter(function(p) { return p.name.indexOf('.') == -1; })
	                    .map(function(param) {
	                    var column = {};
	                    column.data = param.name;
	                    column.title = param.name;
	                    column.defaultContent = '';
	                    column.factory = param.type;
	                    column.render = function(data) {
	                        if (column.factory == 'dict')
	                            return JSON.stringify(data);
	                        else
	                            return data || '';
	                    }
	                    return column;
	                }));

	            $scope.dataTable = $('#example').DataTable( {
	                processing: true,
	                serverSide: true,
	                "columnDefs": [
	                    { className: "center", "targets": [ 0 ] }
	                  ],
	                ajax: function (requestData, callback, settings) {
	                    requestData.page = requestData.start / requestData.length + 1;
	                    requestData.max_results = requestData.length;
	                    var searchTerm = $('input[type=search]').val();
	                    for (var i = 1; i < $scope.columns.length; i++) {
	                        $scope.columns[i]
	                    };

	                    // if (searchTerm && searchTerm.length > 0)
	                    //     requestData.where = ('{"name":{"$regex":"' + $('input[type=search]').val() + '", "$options": "i"}}');

	                    var where = [];
	                    // var search_inputs = $("#example tfoot input");

	                    for (var i = 1; i < $scope.columns.length; i++){
	                        var val = $( "#example tfoot input:eq(" + (i -1) + ")" ).val();
	                        if (val && val.length > 0)
	                            where.push('"' + $scope.columns[i].data + '":{"$regex":"' + val + '", "$options": "i"}');
	                    };

	                    if (where.length > 0)
	                        requestData.where = "{" + where.join(', ') + "}";

	                    if (requestData.order && requestData.order.length > 0) {
	                        sort_field = $scope.columns[requestData.order[0].column].data;
	                        sort_dir = requestData.order[0].dir == 'desc' ? -1 : 1
	                        requestData.sort = '[("' + sort_field + '",' + sort_dir + ')]';
	                    }
	        
	                    $.ajax({
	                        url: 'http://${schemaURL}/${entityName}',
	                        cache: false,
	                        data: requestData,
	                        success: function(data) {
	                            if (data['_meta']) {
	                                data['recordsTotal'] = data['_meta']['total'];
	                                data['iTotalRecords'] = data['_meta']['total'];
	                                data['iTotalDisplayRecords'] = data['_meta']['total'];
	                            }
	                            data['data'] = data['_items'];
	                            callback(data);
	                        }
	                    });
	                },
	                "columns": $scope.columns
	            } );
	            for (var i = 1; i < $scope.columns.length; i++) {
	                $('<td><input type="text" class="searchInput" placeholder="Search ' + $scope.columns[i].data + '" /></td>').appendTo('#example tfoot tr').on( 'keyup change', function () {
	                    // console.log();
	                    $scope.dataTable
	                        .column( i )
	                        .search( $(this).find('input').val() )
	                        .draw();
	                } );
	            };
	        });

	        $('#example').on('click', '.rowCheck', function() {
	            $(this).parents('tr').toggleClass('selected');
	        });

	        $('#example').on('click', '#allCheck', function() {
	            var allCheck = this;
	            $(this).parents('table').find('.rowCheck').each(function() {
	                this.checked = allCheck.checked;
	                if (this.checked)
	                    $(this).parents('tr').addClass('selected');
	                else
	                    $(this).parents('tr').removeClass('selected');
	            });
	        });

	        $('#delete').on('click', function() {
	            var trs = $('#example input[type=checkbox]:checked').parents('tr');
	            var finishedRequests = 0;
	            trs.each(function(i, tr) {
	                var data = $scope.dataTable.row(tr).data();
	                $.ajax({
	                    type: 'POST',
	                    url: data._links.self.href,
	                    headers: {
	                        'X-HTTP-Method-Override': 'DELETE',
	                        'If-Match': data._etag
	                    },
	                    success: function() {
	                        finishedRequests++;
	                        if (finishedRequests == trs.length) {
	                            $scope.dataTable.draw();
	                        }
	                    }
	                });
	            });
	        });

	        $('form').on('click', 'button', function() {
	            var $form = $(this).parents('form');
	            var inputValues = {};
	            var inputs = $form.find('input[type=text]:visible');
	            for (var i = 0; i < inputs.length; i++) {
	                var input = $(inputs[i]);
	                var val = input.val();
	                if (input.attr('factory') == 'dict')
	                    val = JSON.parse(val);
	                inputValues[input.attr('id')] = val;
	            }

	            $.ajax({
	                type: 'POST',
	                data: JSON.stringify(inputValues),
	                url: $form.attr('action'),
	                headers: {
	                    'Content-Type': 'application/json',
	                    'X-HTTP-Method-Override': 'PATCH',
	                    'If-Match': $form.find('#_etag').val()
	                },
	                success: function() {
	                    console.log("success");
	                }
	            });
	            return false;
	        });

	        $('#example').on('click', 'tr', function() {
	            $scope.currentItem = $scope.dataTable.row(this).data();
	            $scope.$digest();
	        });
	    });
	    eveApp.config(['$interpolateProvider', function($interpolateProvider) {
	        $interpolateProvider.startSymbol('{[').endSymbol(']}');
	    }]);
	''')

	content = template.render(schemaURL=eveGrid['schemaURL'], entityName=eveGrid['entityName'], specJsonPath=eveGrid['specJsonPath'])
	page.addJS(jsContent=content)

	params.result = page
	return params


def match(j, args, params, tags, tasklet):
    return True
