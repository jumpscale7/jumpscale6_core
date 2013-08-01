from OpenWizzy import o
import OpenWizzy.portal
import OpenWizzy.baselib.http_client
import unittest

MOUNT_LOCATION = '/opt/data'
SERVERNAME = 'localhost'
USERNAME = 'admin'
PASSWORD = 'admin'
SESSION_DATA = dict()

def setUpModule():
    o.system.fs.createDir(MOUNT_LOCATION)
    data = {'username': USERNAME, 'password': PASSWORD, 'hostname': SERVERNAME, 'mountlocation': MOUNT_LOCATION}
    o.system.process.execute('curlftpfs ftp://%(username)s:%(password)s@%(hostname)s %(mountlocation)s' % data)

def tearDownModule():
    # delete testspace
    o.system.fs.removeDirTree(o.system.fs.joinPaths(MOUNT_LOCATION, 'spaces', SESSION_DATA['spacename']))
    # delete testactor
    o.system.fs.removeDirTree(o.system.fs.joinPaths(MOUNT_LOCATION, 'actors', SESSION_DATA['actorname']))
    # delete testbucket
    o.system.fs.removeDirTree(o.system.fs.joinPaths(MOUNT_LOCATION, 'buckets', SESSION_DATA['bucketname']))

    o.system.process.execute('fusermount -u %s' % MOUNT_LOCATION)

class Tests(unittest.TestCase):
    
    def setUp(self):
        self.client = o.core.portal.getPortalClient('127.0.0.1', 9999, '1234')
        self.contentmanager = self.client.getActor('system', 'contentmanager', instance=0)

    def tearDown(self):
        pass

    def test_1_Mount(self):
        self.assertTrue(o.system.fs.isMount(MOUNT_LOCATION))

    def test_2_createSpace(self):
        SESSION_DATA['spacename'] = o.base.idgenerator.generateGUID()
        spacepath = o.system.fs.joinPaths(MOUNT_LOCATION, 'spaces', SESSION_DATA['spacename'])
        o.system.fs.createDir(spacepath)
        self.assertTrue(o.system.fs.exists(spacepath))
        self.assertIn(SESSION_DATA['spacename'], self.contentmanager.getSpaces())

    def test_3_createActor(self):
        SESSION_DATA['actorname'] = 'system__%s' % o.base.idgenerator.generateGUID()
        actorpath = o.system.fs.joinPaths(MOUNT_LOCATION, 'actors', SESSION_DATA['actorname'])
        o.system.fs.createDir(actorpath)
        self.assertTrue(o.system.fs.exists(actorpath))
        self.assertIn(SESSION_DATA['actorname'], self.contentmanager.getActors())

    def test_3_createBucket(self):
        SESSION_DATA['bucketname'] = o.base.idgenerator.generateGUID()
        bucketpath = o.system.fs.joinPaths(MOUNT_LOCATION, 'buckets', SESSION_DATA['bucketname'])
        o.system.fs.createDir(bucketpath)
        self.assertTrue(o.system.fs.exists(bucketpath))
        self.assertIn(SESSION_DATA['bucketname'], self.contentmanager.getBuckets())

if __name__ == '__main__':
    unittest.main()