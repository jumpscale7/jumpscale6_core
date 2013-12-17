
def main(j, args, params, tags, tasklet):
    params.result = page = args.page
    tags = args.tags

    modifier = j.html.getPageModifierGridDataTables(args.page)
    modifier.prepare4DataTables()
    page.addJS(jsContent='''
    	$(function() {
	    	$('.dataTable').each(function() {
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
	    		table.append(tfoot);
	    	});
	    });
    ''', header=False)

    return params


def match(j, args, params, tags, tasklet):
    return True
