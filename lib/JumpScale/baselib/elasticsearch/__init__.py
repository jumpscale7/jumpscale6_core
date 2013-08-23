from JumpScale import j
from .Elasticsearch import ElasticsearchFactory
from .elasticsearchmanager import ElasticsearchManager
j.base.loader.makeAvailable(j, 'clients')
j.base.loader.makeAvailable(j, 'manage')
j.manage.elasticsearch = ElasticsearchManager()
j.clients.elasticsearch = ElasticsearchFactory()
