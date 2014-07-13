from JumpScale import j

from pymongo import MongoClient

class MongoDBClient:

    def get(self, host='localhost', port=27017):
        try:
            client = MongoClient(host, port)
        except:
            raise RuntimeError('Could not connect to mongodb server on %s:%s' % (host, port))
        else:
            return client

