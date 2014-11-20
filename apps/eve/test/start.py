from JumpScale import j
import os

import mongoengine
from eve import Eve
from eve.render import send_response
from eve_mongoengine import EveMongoengine

from flask.ext.bootstrap import Bootstrap
from eve_docs import eve_docs
from eve_docs.config import get_cfg

# create some dummy model class

# default eve settings
my_settings = {
	'MONGO_HOST': 'localhost',
	'MONGO_PORT': 27017,
	'MONGO_DBNAME': 'js_system',
        #'ID_FIELD': '_id',
	'DOMAIN': {}, # sadly this is needed for eve
	'RESOURCE_METHODS': ['GET', 'POST'],
	'ITEM_METHODS': ['GET', 'PATCH', 'PUT', 'DELETE'],
	'X_DOMAINS': '*',
	'MONGO_QUERY_BLACKLIST': [],
	'X_HEADERS': ["X-HTTP-Method-Override", 'If-Match']
}

if not os.path.exists('generated/system.py'):
	import JumpScale.grid.osis

	client = j.core.osis.getClientByInstance('main')
	json=client.getOsisSpecModel("system")

	from generators.MongoEngineGenerator import *

	gen=MongoEngineGenerator("generated/system.py")
	gen.generate(json)

my_settings['DOMAIN'] = {
	'eco': {
		'item_url': 'regex("[a-f0-9]+")', 
		'item_lookup_field': '_id', 
		'schema': {
			'_id': {'type': 'string'},
			'code': {'required': True, 'type': 'string'}, 
			'extra': {'required': True, 'type': 'string'}, 
			'backtrace': {'required': True, 'type': 'string'}, 
			'pid': {'required': True, 'type': 'integer'}, 
			'occurrences': {'required': True, 'type': 'integer'}, 
			'backtracedetailed': {'required': True, 'type': 'string'}, 
			'category': {'required': True, 'type': 'string'}, 
			'jid': {'required': True, 'type': 'integer'}, 
			'appname': {'required': True, 'type': 'string'}, 
			'epoch': {'required': True, 'type': 'integer'}, 
			'funclinenr': {'required': True, 'type': 'integer'}, 
			'state': {'required': True, 'type': 'string'}, 
			'gid': {'required': True, 'type': 'integer'}, 
			'type': {'required': True, 'type': 'string'}, 
			'funcfilename': {'required': True, 'type': 'string'}, 
			'errormessagepub': {'required': True, 'type': 'string'}, 
			'tags': {'required': True, 'type': 'string'}, 
			'closetime': {'required': True, 'type': 'integer'}, 
			'nid': {'required': True, 'type': 'integer'}, 
			'lasttime': {'required': True, 'type': 'integer'}, 
			'level': {'required': True, 'type': 'integer'}, 
			'errormessage': {'required': True, 'type': 'string'}, 
			'funcname': {'required': True, 'type': 'string'}, 
			'aid': {'required': True, 'type': 'integer'}, 
			'masterjid': {'required': True, 'type': 'integer'}
		}, 
		'item_methods': ['GET', 'PATCH', 'PUT', 'DELETE'], 
		'resource_methods': ['GET', 'POST', 'DELETE'], 
		'url': 'eco', 
	}
}

# init application
app = Eve(__name__, settings=my_settings)
# init extension
# ext = EveMongoengine(app)
# register model to eve

from generated.system import *

# for classs in classes:
#     ext.add_model(classs)

# Eve_mongoengine doesn't support different _id fields, although Eve does.
# The workaround is to override the generated Eve schema
# for entity in ['eco']:
# 	ext.app.settings['DOMAIN'][entity]['item_url'] = 'regex("[a-f0-9]+")'
# 	ext.app.settings['DOMAIN'][entity]['schema']['_id'] = {'type': 'string'}

Bootstrap(app)

@app.route('/ui')
def ui():
    return render_template('ui.html')


# Unfortunately, eve_docs doesn't support CORS (too bad!), so we had to reimplement it ourselves
@app.route('/docs/spec.json')
def specs():
    return send_response(None, [get_cfg()])

print "visit:\nhttp://localhost:5000/docs/"

# let's roll
app.run('0.0.0.0', debug=True)




