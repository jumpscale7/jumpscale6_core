from JumpScale import j
import JumpScale.portal
import JumpScale.baselib.http_client
import unittest

MOUNT_LOCATION = '/opt/data'
SERVERNAME = 'localhost'
USERNAME = 'admin'
PASSWORD = 'admin'
SESSION_DATA = dict()


def setUpModule():
    j.system.fs.createDir(MOUNT_LOCATION)
    data = {'username': USERNAME, 'password': PASSWORD, 'hostname': SERVERNAME, 'mountlocation': MOUNT_LOCATION}
    j.system.process.execute('curlftpfs ftp://%(username)s:%(password)s@%(hostname)s %(mountlocation)s' % data)


def tearDownModule():
    # delete testspace
    j.system.fs.removeDir(j.system.fs.joinPaths(MOUNT_LOCATION, 'spaces', SESSION_DATA['spacename']))
    # delete testactor
    j.system.fs.removeDir(j.system.fs.joinPaths(MOUNT_LOCATION, 'actors', SESSION_DATA['actorname']))
    # delete testbucket
    j.system.fs.removeDir(j.system.fs.joinPaths(MOUNT_LOCATION, 'buckets', SESSION_DATA['bucketname']))

    j.system.process.execute('fusermount -u %s' % MOUNT_LOCATION)


class Tests(unittest.TestCase):

    def setUp(self):
        self.client = j.core.portal.getPortalClient('127.0.0.1', 9999, '1234')
        self.contentmanager = self.client.getActor('system', 'contentmanager', instance=0)

    def tearDown(self):
        pass

    def test_1_Mount(self):
        self.assertTrue(j.system.fs.isMount(MOUNT_LOCATION))

    def test_2_createSpace(self):
        SESSION_DATA['spacename'] = j.base.idgenerator.generateGUID()
        spacepath = j.system.fs.joinPaths(MOUNT_LOCATION, 'spaces', SESSION_DATA['spacename'])
        j.system.fs.createDir(spacepath)
        self.assertTrue(j.system.fs.exists(spacepath))
        self.assertIn(SESSION_DATA['spacename'], self.contentmanager.getSpaces())

    def test_3_createActor(self):
        SESSION_DATA['actorname'] = 'system__%s' % j.base.idgenerator.generateGUID()
        actorpath = j.system.fs.joinPaths(MOUNT_LOCATION, 'actors', SESSION_DATA['actorname'])
        j.system.fs.createDir(actorpath)
        self.assertTrue(j.system.fs.exists(actorpath))
        self.assertIn(SESSION_DATA['actorname'], self.contentmanager.getActors())

    def test_3_createBucket(self):
        SESSION_DATA['bucketname'] = j.base.idgenerator.generateGUID()
        bucketpath = j.system.fs.joinPaths(MOUNT_LOCATION, 'buckets', SESSION_DATA['bucketname'])
        j.system.fs.createDir(bucketpath)
        self.assertTrue(j.system.fs.exists(bucketpath))
        self.assertIn(SESSION_DATA['bucketname'], self.contentmanager.getBuckets())

    def test_4_createActorMethod(self):
        self.assertIn(SESSION_DATA['actorname'], self.contentmanager.getActors())
        j.system.fs.renameFile(j.system.fs.joinPaths(MOUNT_LOCATION, 'actors', SESSION_DATA['actorname'], 'specs', 'example__ActorModel.spec'), j.system.fs.joinPaths(
            MOUNT_LOCATION, 'actors', SESSION_DATA['actorname'], 'specs', 'model.spec'))
        j.system.fs.renameFile(j.system.fs.joinPaths(MOUNT_LOCATION, 'actors', SESSION_DATA['actorname'], 'specs', 'example__Actor.spec'), j.system.fs.joinPaths(
            MOUNT_LOCATION, 'actors', SESSION_DATA['actorname'], 'specs', 'actor.spec'))
        j.system.fs.createDir(j.system.fs.joinPaths(MOUNT_LOCATION, 'actors', SESSION_DATA['actorname'], 'methodclass'))
        actorparts = SESSION_DATA['actorname'].split('__')
        osisfilename = '%s_osis' % '_'.join(actorparts)
        osisfile = """
        from JumpScale import j
        class %s(j.code.classGetBase()):
            def __init__(self):
                self.dbmem=j.db.keyvaluestore.getMemoryStore()
                self.db=self.dbmem

        """ % osisfilename

        methodsfile = """
        from JumpScale import j
        from %(osisfilename)s import %(osisfilename)s

        class %(actorclassname)s(%(osisfilename)s):
            def __init__(self):
                self._te={}
                self.actorname=%(actorname)s
                self.appname=%(appname)s
                 %(osisfilename)s.__init__(self)

            def dosomething(self, path, id, bool):
                return True

            def returnlist(self):
                return [1, 2, 3]

        """ % {'osisfilename': osisfilename, 'actorclassname': '_'.join(actorparts), 'actorname': actorparts[1], 'appname': actorparts[0]}
        j.system.fs.writeFile(j.system.fs.joinPaths(MOUNT_LOCATION, 'actors', SESSION_DATA['actorname'], 'methodclass', '%s.py' % osisfilename), osisfile)
        j.system.fs.writeFile(j.system.fs.joinPaths(MOUNT_LOCATION, 'actors', SESSION_DATA[
                              'actorname'], 'methodclass', '%s.py' % '_'.join(actorparts)), methodsfile)

if __name__ == '__main__':
    unittest.main()
