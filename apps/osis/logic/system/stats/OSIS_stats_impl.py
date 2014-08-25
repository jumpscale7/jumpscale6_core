from JumpScale import j
from JumpScale.grid.osis.OSISStore import OSISStore

ujson = j.db.serializers.getSerializerType('j')

MONITORING_DB_NAME = 'monitoring'

class mainclass(OSISStore):

    def __init__(self, dbconnections):
        self.elasticsearch = None
        self.dbclient = dbconnections['influxdb_main']
        databases = [db['name'] for db in self.dbclient.get_database_list()]
        if MONITORING_DB_NAME not in databases:
            self.dbclient.create_database(MONITORING_DB_NAME)

    def set(self, key, stats, waitIndex=False, session=None):
        data = {'name': key, 'points': []}
        for stat in stats:
            if 'columns' not in data:
                data['columns'] = stat.keys()
            data['points'].append(stat.values())
        self.dbclient.write_points([data])

    def delete(self, seriesName, session=None):
        self.dbclient.delete_series(seriesName)

    def find(self, query, start=0, size =100, session=None):
        return self.dbclient.query(query)

    def destroyindex(self, session=None):
        raise RuntimeError("osis 'destroyindex' for stat not implemented")

    def getIndexName(self):
        return "system_stats"

    def get(self,key, session=None):
        raise RuntimeError("osis 'get' for stat not implemented")

    def exists(self,key, session=None):
        raise RuntimeError("osis exists for stat not implemented")
        #work with elastic search only


    #NOT IMPLEMENTED METHODS WHICH WILL NEVER HAVE TO BE IMPLEMENTED

    def setObjIds(self,**args):
        raise RuntimeError("osis method setObjIds is not relevant for stats namespace")

    def rebuildindex(self,**args):
        raise RuntimeError("osis method rebuildindex is not relevant for stats namespace")

    def list(self,**args):
        raise RuntimeError("osis method list is not relevant for stats namespace")

    def removeFromIndex(self,**args):
        raise RuntimeError("osis method removeFromIndex is not relevant for stats namespace")

