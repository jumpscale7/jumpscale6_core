from OpenWizzy import o
from .Elasticsearch import ElasticsearchFactory
from .elasticsearchmanager import ElasticsearchManager
o.base.loader.makeAvailable(o, 'clients')
o.base.loader.makeAvailable(o, 'manage')
o.manage.elasticsearch = ElasticsearchManager()
o.clients.elasticsearch = ElasticsearchFactory()
