
def main(j, args, params, tags, tasklet):
	page = args.page

	hrd = j.core.hrd.getHRD(content=args.cmdstr)
	eveGrid = {}
	eveGrid['schemaURL'] = getattr(hrd, 'schema_url', '')
	eveGrid['specJsonPath'] = getattr(hrd, 'spec_json_path', '/docs/spec.json')
	eveGrid['entityName'] = getattr(hrd, 'entity_name', '')

	# Add our static resources only once to the page
	if '/jslib/jquery/jqueryDataTable/css/dataTables.bootstrap.css' not in str(page):
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
		

		page.addJS('/jslib/jquery/jqueryDataTable/js/jquery.dataTables.js')
		page.addJS('/jslib/angular/angular1-3-0.min.js')
		page.addJS('/jslib/bootstrap/js/bootstrap.min.js')
		page.addJS('/jslib/underscore/underscore-min.js')
		page.addJS('/jslib/jquery/jqueryDataTable/js/dataTables.bootstrap.js')
		
		import jinja2
		jinja = jinja2.Environment(variable_start_string="${", variable_end_string="}")

		template = '''
			var eveModule = angular.module('eveModule', []);
			eveModule.directive('eveGrid', function($http) {
		      return {
			      restrict: 'EA',
			      scope: true,
			      link: function (scope, element, attrs, ctrl) {
			      	console.log(attrs);
			      	$http({
		             url: 'http://' + attrs['eveUrl'] + attrs['eveSpecPath'],
		             method: 'GET',

		             }).then(function(data) {
			            scope.schema = data.data;
			      		
			            scope.columns = [{data: null, orderable: false, defaultContent: '<input class="rowCheck" type="checkbox"></input>', 'title': '<input class="allCheck" type="checkbox"></input>'}]
			                .concat(scope.schema.domains[attrs["eveEntity"]]['/' + attrs["eveEntity"]].POST.params
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
						
			            scope.dataTable = $('#' + attrs["eveEntity"] + '-container table').DataTable( {
			                processing: true,
			                serverSide: true,
			                "columnDefs": [
			                    { className: "center", "targets": [ 0 ] }
			                  ],
			                ajax: function (requestData, callback, settings) {
			                    requestData.page = requestData.start / requestData.length + 1;
			                    requestData.max_results = requestData.length;
			                    var searchTerm = $('input[type=search]').val();
			                    for (var i = 1; i < scope.columns.length; i++) {
			                        scope.columns[i]
			                    };

			                    var where = [];

			                    for (var i = 1; i < scope.columns.length; i++){
			                        var val = $( '#' + attrs["eveEntity"] + '-container table tfoot input:eq(' + (i -1) + ')' ).val();
			                        if (val && val.length > 0)
			                            where.push('"' + scope.columns[i].data + '":{"$regex":"' + val + '", "$options": "i"}');
			                    };

			                    if (where.length > 0)
			                        requestData.where = "{" + where.join(', ') + "}";

			                    if (requestData.order && requestData.order.length > 0) {
			                        sort_field = scope.columns[requestData.order[0].column].data;
			                        sort_dir = requestData.order[0].dir == 'desc' ? -1 : 1
			                        requestData.sort = '[("' + sort_field + '",' + sort_dir + ')]';
			                    }

			                    $.ajax({
			                        url: 'http://' + attrs['eveUrl'] + '/' + attrs["eveEntity"],
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
			                "columns": scope.columns
			            } );
			            for (var i = 1; i < scope.columns.length; i++) {
			                $('<td><input type="text" class="searchInput" placeholder="Search ' + scope.columns[i].data + '" /></td>').appendTo('#' + attrs["eveEntity"] + '-container table tfoot tr').on( 'keyup change', function () {
			                    scope.dataTable
			                        .column( i )
			                        .search( $(this).find('input').val() )
			                        .draw();
			                } );
			            };
			        });

			        $('#' + attrs["eveEntity"] + '-container table').on('click', '.rowCheck', function() {
			            $(this).parents('tr').toggleClass('selected');
			        });

			        $('#' + attrs["eveEntity"] + '-container table').on('click', '.allCheck', function() {
			            var allCheck = this;
			            $(this).parents('table').find('.rowCheck').each(function() {
			                this.checked = allCheck.checked;
			                if (this.checked)
			                    $(this).parents('tr').addClass('selected');
			                else
			                    $(this).parents('tr').removeClass('selected');
			            });
			        });

			        $('#' + attrs["eveEntity"] + '-container table .delete').on('click', function() {
			            var trs = $('#' + attrs["eveEntity"] + '-container table input[type=checkbox]:checked').parents('tr');
			            var finishedRequests = 0;
			            trs.each(function(i, tr) {
			                var data = scope.dataTable.row(tr).data();
			                $.ajax({
			                    type: 'POST',
			                    url: 'http://' + attrs['eveUrl'] + '/' + attrs["eveEntity"] + '/'+ data._id,
			                    headers: {
			                        'X-HTTP-Method-Override': 'DELETE',
			                        'If-Match': data._etag
			                    },
			                    success: function() {
			                        finishedRequests++;
			                        if (finishedRequests == trs.length) {
			                            scope.dataTable.draw();
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

			        $('#' + attrs["eveEntity"] + '-container table').on('click', 'tr', function() {
			            scope.currentItem = scope.dataTable.row(this).data();
			            scope.$digest();
			        });
			      },
			      template:'<table id="example" class="table table-striped" cellspacing="0" width="100%"><tfoot><tr><td><button class="delete btn btn-primary">Delete</button></td></tr></tfoot></table>'
		    }
		    });
		'''

		content = template
		page.addJS(jsContent=content)

	


	page.addMessage('''
		<div class="container">
	        <eveGrid id="{entityName}-container" eve-grid eve-url="{schemaURL}" eve-entity="{entityName}" eve-spec-path="{specJsonPath}">
	       	</eveGrid>
    	</div>
	 '''.format(**eveGrid))

	params.result = page
	return params


def match(j, args, params, tags, tasklet):
    return True
