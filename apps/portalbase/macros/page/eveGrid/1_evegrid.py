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
	}

	eveGrid['columns'] = []
	for i in count(1):
		column = {}
		column['data'] = hrd.get('column.{}.data'.format(i), default='')
		if not column['data']:
			break
		column['header'] = hrd.get('column.{}.header'.format(i), default='')
		column['format'] = hrd.get('column.{}.format'.format(i), default='')
		eveGrid['columns'].append(column)
	
	# import ipdb; ipdb.set_trace()
	eveGrid['columns'] = (json.dumps(eveGrid['columns']))


	# Add our static resources only once to the page
	if '/system/.files/lib/evegrid/css/eve-grid.css' not in str(page):
		page.addCSS('/jslib/jquery/jqueryDataTable/css/dataTables.bootstrap.css')
		page.addCSS('/jslib/jquery/jqueryDataTable/css/bootstrap-theme.min.css')
		page.addCSS('/system/.files/lib/evegrid/css/eve-grid.css')
		page.addCSS('https://rawgit.com/Eonasdan/bootstrap-datetimepicker/master/build/css/bootstrap-datetimepicker.min.css')

		page.addJS('/jslib/jquery/jqueryDataTable/js/jquery.dataTables.js')
		page.addJS('/jslib/angular/angular1-3-0.min.js')
		page.addJS('/jslib/bootstrap/js/bootstrap.min.js')
		page.addJS('/jslib/underscore/underscore-min.js')
		page.addJS('/jslib/jquery/jqueryDataTable/js/dataTables.bootstrap.js')
		page.addJS('/jslib/moment.js')
		page.addJS('https://rawgit.com/Eonasdan/bootstrap-datetimepicker/master/src/js/bootstrap-datetimepicker.js')

		page.addJS('/system/.files/lib/evegrid/js/eve-grid.js')
	
	page.addMessage('''
		<div class="container eve-grid-container">
	        <div id="{entityName}-container" eve-grid eve-url="{schemaURL}" eve-entity="{entityName}" eve-spec-path="{specJsonPath}" datetime-fields={datetimeFields} columns='{columns}'>
	       	</div>
    	</div>

	 '''.format(**eveGrid))
	params.result = page
	return params


def match(j, args, params, tags, tasklet):
    return True
