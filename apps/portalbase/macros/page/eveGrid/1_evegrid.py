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
	if '/jslib/jquery/jqueryDataTable/css/eve-grid.css' not in str(page):
		page.addCSS('/jslib/bootstrap/css/bootstrap.css')
		page.addCSS('/jslib/jquery/jqueryDataTable/css/dataTables.bootstrap.css')
		page.addCSS('/jslib/jquery/jqueryDataTable/css/bootstrap-theme.min.css')
		page.addCSS('/jslib/jquery/jqueryDataTable/css/eve-grid.css')
		page.addCSS('/jslib/jquery/jquery-ui.structure.min.css')
		page.addCSS('//cdnjs.cloudflare.com/ajax/libs/jqueryui/1.11.2/jquery-ui.theme.min.css')

		page.addJS('/jslib/jquery/jqueryDataTable/js/jquery.dataTables.js')
		page.addJS('/jslib/angular/angular1-3-0.min.js')
		page.addJS('/jslib/bootstrap/js/bootstrap.min.js')
		page.addJS('/jslib/underscore/underscore-min.js')
		page.addJS('/jslib/jquery/jqueryDataTable/js/dataTables.bootstrap.js')
		page.addJS('/jslib/moment.js')
		page.addJS('/jslib/jquery/jquery-ui.min.js')
		page.addJS('/jslib/jquery/jquery-ui-sliderAccess.js')		
		page.addJS('/jslib/jquery/jquery-ui-timepicker-addon.min.js')
		page.addJS('/jslib/jquery/jqueryDataTable/js/eve-grid.js')
	
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