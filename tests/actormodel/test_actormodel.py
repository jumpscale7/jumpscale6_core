import requests
import json
import unittest
import os
import uuid
import subprocess
import logging
import threading

from OpenWizzy import o

def setUp():
    o.application.start('actortest')

def tearDown():
    o.application.stop()

debug = True
out = err = None

appport = 9099
if debug:
    appport = 80

baseurl = 'http://localhost:%s/restmachine/space/objects/model.%%s' % appport
baserestfull = 'http://localhost:%s/restextmachine/space/objects/%%s' % appport
loginurl = "http://localhost:%s" % appport
appdir = os.path.join(o.dirs.appDir, str(uuid.uuid4()))
procs = list()

class LogPipe(threading.Thread):

    def __init__(self, level):
        """Setup the object with a logger and a loglevel
        and start the thread
        """
        threading.Thread.__init__(self)
        self.daemon = False
        self.level = level
        self.fdRead, self.fdWrite = os.pipe()
        self.pipeReader = os.fdopen(self.fdRead)
        self.start()

    def fileno(self):
        """Return the write file descriptor of the pipe
        """
        return self.fdWrite

    def run(self):
        """Run the thread, logging everything.
        """
        for line in iter(self.pipeReader.readline, ''):
            logging.log(self.level, line.strip('\n'))

        self.pipeReader.close()

    def close(self):
        """Close the write end of the pipe.
        """
        os.close(self.fdWrite)


def setUp():
    app = os.path.join(os.path.dirname(__file__), '_app')
    o.system.fs.copyDirTree(app, appdir)
    if not debug:
        global out, err
        out = LogPipe(logging.INFO)
        err = LogPipe(logging.ERROR)
        startOsis(out, err)
        startApp(out, err)


def startOsis(out, err):
    import ipdb; ipdb.set_trace()
    path = o.system.fs.joinPaths(o.dirs.baseDir, 'apps', 'osis')
    proc = subprocess.Popen(['python', 'osisServerStart.py'], cwd=path, stdout=out, stderr=err)
    procs.append(proc)

def startApp(out, err):
    proc = subprocess.Popen(['python', 'start_appserver.py'], cwd=appdir, stdout=out, stderr=err)
    procs.append(proc)
    o.system.net.waitConnectionTest('127.0.0.1', appport, 5)


def tearDown():
    for proc in procs:
        proc.kill()
    o.system.fs.removeDirTree(appdir)
    global out, err
    if out:
        out.close()
    if err:
        err.close()


class RestMachine(unittest.TestCase):
    objecttype = 'machine'
    objectpk = 'id'
    idtype = int

    def setUp(self):
        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json'}
        self.session = requests.Session()
        self.login('admin', 'admin')
        self.ids = list()


    def tearDown(self):
        for id in self.ids[:]:
            try:
                self.delete(id)
            except:
                print 'Failed to delete possibly already deleted'

    def login(self, username, password):
        data = {'passwd': password,
                'user_login_': username}
        self.session.post(loginurl, data=json.dumps(data), headers=self.headers)

    def doRequest(self, action, data=None, method='post'):
        url = '%s.%s' % (baseurl % self.objecttype, action)
        data = json.dumps(data)
        req = getattr(self.session, method, self.session.post)
        r = req(url, data=data, headers=self.headers)
        self.assertEqual(r.status_code, 200)
        return r

    def test_create(self):
        data = {'name': 'test', 'memory': 6}
        if self.idtype is basestring:
            data['id'] = str(uuid.uuid4())
        r = self.doRequest('create', data)
        id = r.json()
        self.assertTrue(id)
        self.assertIsInstance(id, self.idtype)
        self.ids.append(id)
        return id

    def list(self):
        return self.doRequest('list').json()

    def test_list(self):
        id = self.test_create()
        result = self.list()
        self.assertIn(str(id), result)
        return result, id

    def delete(self, id):
        self.doRequest('delete', {'id': id})
        self.ids.remove(id)

    def test_delete(self):
        id = self.test_create()
        self.delete(id)
        result = self.list()
        self.assertNotIn(str(id), result)

    def get(self, id):
        rawobj = self.doRequest('get', {'id': id}).json()
        return rawobj

    def test_get(self):
        id = self.test_create()
        obj = self.get(id)
        self.assertIsInstance(obj, dict)
        for prop in ('guid', 'memory', 'name'):
            self.assertIn(prop, obj)
        return obj

    def test_update(self):
        obj = self.test_get()
        update = {self.objectpk: obj[self.objectpk], 'memory': 2048}
        self.doRequest('set', {'data': update})
        newobj = self.get(obj[self.objectpk])
        self.assertEqual(newobj['memory'], update['memory'])
        self.assertEqual(newobj['name'], obj['name'])


class RestExtMachine(RestMachine):

    def doRequest(self, action, data=None, method='post'):
        req = self.session.get
        url = baserestfull % self.objecttype
        jsondata = None
        if action == 'create':
            jsondata = json.dumps(data)
            req = self.session.post
        elif action == 'set':
            jsondata = json.dumps(data)
            req = self.session.put
            url += '/%s' % data['data'][self.objectpk]
        elif action == 'delete':
            req = self.session.delete
            url += '/%s' % data['id']
        elif action == 'get':
            url += '/%s' % data['id']

        r = req(url, data=jsondata, headers=self.headers)
        self.assertEqual(r.status_code, 200)
        return r

class RestMachineOsis(RestMachine):
    objecttype = 'machineosis'

class RestMachineExtOsis(RestExtMachine):
    objecttype = 'machineosis'

class RestNic(RestMachine):
    objecttype = 'nic'
    idtype = basestring

class RestExtNic(RestExtMachine):
    objecttype = 'nic'
    idtype = basestring

class RestNicOsis(RestMachine):
    objecttype = 'nicosis'
    idtype = basestring

class RestExtNicOsis(RestExtMachine):
    objecttype = 'nicosis'
    idtype = basestring


