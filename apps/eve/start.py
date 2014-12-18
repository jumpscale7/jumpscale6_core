from JumpScale import j
import os

from eve import Eve
from eve.render import send_response

from flask.ext.bootstrap import Bootstrap
from eve_docs import eve_docs
from eve_docs.config import get_cfg
from generators.EveGenerator import generateDomain
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple
from flask import render_template


# default eve settings
import JumpScale.grid.osis
client = j.core.osis.getClientByInstance('main')

apps = dict()

for namespace in client.listNamespaces():
    spec=client.getOsisSpecModel(namespace)
    dbname = namespace if namespace != 'system' else 'js_system'
    my_settings = {
            'MONGO_HOST': 'localhost',
            'MONGO_PORT': 27017,
            'MONGO_DBNAME': dbname,
            'DOMAIN': generateDomain(spec),
            'RESOURCE_METHODS': ['GET', 'POST'],
            'ITEM_METHODS': ['GET', 'PATCH', 'PUT', 'DELETE'],
            'X_DOMAINS': '*',
            'MONGO_QUERY_BLACKLIST': [],
            'X_HEADERS': ["X-HTTP-Method-Override", 'If-Match']
    }

    # init application
    app = Eve(__name__, settings=my_settings)

    Bootstrap(app)

    @app.route('/ui')
    def ui():
        return render_template('ui.html')

    # Unfortunately, eve_docs doesn't support CORS (too bad!), so we had to reimplement it ourselves
    @app.route('/docs/spec.json')
    def specs():
        return send_response(None, [get_cfg()])

    apps['/%s' % namespace] = app 

print "visit:\nhttp://localhost:5000/docs/"
if apps:
    firstapp = apps.values()[0]
    application = DispatcherMiddleware(firstapp, apps)
# let's roll
    run_simple('0.0.0.0', 5000, application, use_reloader=True)




