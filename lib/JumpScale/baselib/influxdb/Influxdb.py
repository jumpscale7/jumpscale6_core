from JumpScale import j
import redis
from influxdb import client as influxdb

class InfluxdbFactory:

    """
    """

    def __init__(self):
        pass

    def get(self, host='localhost', port=8086,username='root', password='root', database=None, ssl=False, verify_ssl=False, timeout=None, use_udp=False, udp_port=4444):
        db = influxdb.InfluxDBClient(host=host, port=port,username=username, password=password, database=database, ssl=ssl, \
            verify_ssl=verify_ssl, timeout=timeout, use_udp=use_udp, udp_port=udp_port)
        return db

    def getByInstance(self, name):
        jp=j.packages.findNewest(name="influxdb_client",domain="serverapps")
        jp=jp.load(name)
        if not jp.isInstalled():
            j.events.opserror_critical("No instance influxdb_client %s."% name)
        hrd = jp.hrd_instance
        ipaddr = hrd.get("influxdb.client.addr")
        port = hrd.getInt("influxdb.client.port")        
        login = hrd.get("influxdb.client.login")
        passwd = hrd.get("influxdb.client.passwd")
        client = self.get(host=ipaddr, port=port,username=login, password=passwd, database="main")
        return client
