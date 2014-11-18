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
	'MONGO_DBNAME': 'eve',
	'DOMAIN': {}, # sadly this is needed for eve
	#'RESOURCE_METHODS': ['GET', 'POST'],
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

# init application
app = Eve(__name__, settings=my_settings)
# init extension
ext = EveMongoengine(app)
# register model to eve

from generated.system import *

for classs in classes:
    ext.add_model(classs)

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

