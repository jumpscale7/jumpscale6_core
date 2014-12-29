from itertools import count
import json

def main(j, args, params, tags, tasklet):
	page = args.page
	
	hrd = j.core.hrd.getHRD(content=args.cmdstr)

	eveGrid = {
		'specJsonPath': hrd.get('spec_json_path', default='/docs/spec.json'),
		'schemaURL': hrd.get('schema_url', default=''),
		'entityName': hrd.get('entity_name', default=''),
		'datetimeFields': hrd.get('datetime_fields', default=''),
		'sort_by':hrd.get('sort_by', default='') # Mongo syntax : [("guid", -1), ("pid", 1),]
	}

	eveGrid['columns'] = []
	
	hrd_data = sorted(list(hrd.prefix('column')))
	
	data = [e for e in hrd_data if e.endswith('data')]

	for e in data:
		column = {}
		prefix = e[:-5]
		
		data = '%s.data' % prefix
		header = '%s.header' % prefix
		format = '%s.format' % prefix
		
		column['data'] = hrd.get(data, default='')
		column['header'] = hrd.get(header, default=prefix)
		column['format'] = hrd.get(format, default='')
		
		eveGrid['columns'].append(column)

	# import ipdb; ipdb.set_trace()

	eveGrid['columns'] = (json.dumps(eveGrid['columns']))
	
	# Add our static resources only once to the page
	if '/system/.files/lib/evegrid/css/eve-grid.css' not in str(page):
		page.addCSS('/jslib/jquery/jqueryDataTable/css/dataTables.bootstrap.css')
		page.addCSS('/jslib/jquery/jqueryDataTable/css/bootstrap-theme.min.css')
		page.addCSS('/system/.files/lib/evegrid/css/eve-grid.css')
		page.addCSS('/jslib/bootstrap/css/bootstrap-datetimepicker.min.css')
		page.addCSS('/jslib/bootstrap/css/bootstrap-3.2.min.css')
		page.addJS('/jslib/jquery/jqueryDataTable/js/jquery.dataTables.js')
		page.addJS('/jslib/angular/angular1-3-0.min.js')
		page.addJS('/jslib/bootstrap/js/bootstrap.min.js')
		page.addJS('/jslib/underscore/underscore-min.js')
		page.addJS('/jslib/jquery/jqueryDataTable/js/dataTables.bootstrap.js')
		page.addJS('/jslib/moment.js')
		page.addJS('/jslib/bootstrap/js/bootstrap-datetimepicker.js')
		page.addJS('/jslib/spin.min.js')
		page.addJS('/system/.files/lib/evegrid/js/eve-grid.js')
	
	page.addMessage('''
		<div class="container eve-grid-container">
	        <div id="{entityName}-container" eve-grid eve-url="{schemaURL}" eve-entity="{entityName}" eve-spec-path="{specJsonPath}" datetime-fields={datetimeFields} columns='{columns}'>
	       	</div>
	    	<div id="confirmModal" class="modal fade">
			    <div class="modal-dialog">
			        <div class="modal-content">
			            <div class="modal-header">
			                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
			                <h4 class="modal-title">Confirmation</h4>
			            </div>
			            <div class="modal-body">
			                <p>Are you sure you want to delete?</p>
			            </div>
			            <div class="modal-footer">
			                <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
			                <button type="button" class="btn btn-danger confirmDelete">Delete</button>
			            </div>
			        </div>
			    </div>
			</div>
    	</div>

	 '''.format(**eveGrid))
	params.result = page
	return params


def match(j, args, params, tags, tasklet):
    return True
