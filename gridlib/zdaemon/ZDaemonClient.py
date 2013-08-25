from JumpScale import j
import JumpScale.baselib.serializers
import zmq
import time
import struct
import math
from random import randrange


class Session():

    def __init__(self, id, organization, user, passwd, encrkey, netinfo, roles):
        self.id = id
        self.encrkey = encrkey
        self.user = user
        self.passwd = passwd
        self.organization = organization
        self.netinfo = netinfo
        self.start = int(time.time())
        self.roles = roles

    def __repr__(self):
        return str(self.__dict__)

    __str__ = __repr__


class ZDaemonClient():

    def __init__(self, ipaddr="localhost", port=4444, org="myorg", user="root", passwd="passwd", ssl=False, datachannel=False, encrkey="", reset=False, roles=[]):
        """
        @param encrkey (use for simple blowfish shared key encryption, better to use SSL though, will do the same but dynamically exchange the keys)
        """
        self.retry = True
        self.port = port
        self.ipaddr = ipaddr
        self.datachannel = datachannel
        self.id = ""
        self.init()
        self.blocksize = 8 * 1024 * 1024
        self.key = encrkey
        self.user = user
        self.org = org
        self.passwd = passwd
        self.ssl = ssl
        self.roles = roles
        self.keystor = None
        self.initSession(reset, ssl)

    def initSession(self, reset=False, ssl=False):

        if ssl:
            from JumpScale.baselib.ssl.SSL import SSL
            self.keystor = SSL().getSSLHandler()
            try:
                self.keystor.getPrivKey(self.org, self.user)
            except:
                # priv key now known yet
                reset = True

            if reset:
                self.keystor.createKeyPair(organization=self.org, user=self.user)

            pubkey = self.keystor.getPubKey(organization=self.org, user=self.user, returnAsString=True)
            self.sendcmd(cmd="registerpubkey", sendformat='m', returnformat='', organization=self.org, user=self.user, pubkey=pubkey)

            self.pubkeyserver = self.sendcmd(cmd="getpubkeyserver", sendformat='m', returnformat='')

            # generate unique key
            encrkey = ""
            for i in range(56):
                encrkey += chr(randrange(0, 256))

            # only encrypt the key & the passwd, the rest is not needed
            encrkey = self.keystor.encrypt(self.org, self.user, "", "", message=encrkey, sign=True, base64=True, pubkeyReader=self.pubkeyserver)
            passwd = self.keystor.encrypt(self.org, self.user, "", "", message=self.passwd, sign=True, base64=True, pubkeyReader=self.pubkeyserver)

        else:
            encrkey = ""
            passwd = self.passwd

        session = Session(id=self.id, organization=self.org, user=self.user, passwd=passwd,
                          encrkey=encrkey, netinfo=j.system.net.getNetworkInfo(), roles=self.roles)
        ser = j.db.serializers.getMessagePack()
        sessiondictstr = ser.dumps(session.__dict__)
        self.key = session.encrkey

        self.sendcmd(cmd="registersession", sendformat='m', returnformat='', data=sessiondictstr, ssl=ssl)

    def init(self):
        j.logger.log("check server is reachable on %s on port %s" % (self.ipaddr, self.port), level=4, category='zdaemon.client.init')
        res = j.system.net.waitConnectionTest(self.ipaddr, self.port, 20)

        # 12 bytes unique id
        end = 4294967295  # 4bytes max nr
        self.id = struct.pack("<III", j.base.idgenerator.generateRandomInt(
            1, end), j.base.idgenerator.generateRandomInt(1, end), j.base.idgenerator.generateRandomInt(1, end))

        if res == False:
            msg = "Could not find a running server instance  on %s:%s" % (self.ipaddr, self.port)
            j.errorconditationhandler.raiseOperationalCritical(msgpub=msg, message="", category="zdaemonclient.init", die=True)
        j.logger.log("server is reachable on %s on port %s" % (self.ipaddr, self.port), level=4, category='zdaemon.client.init')

        self.context = zmq.Context()

        self.cmdchannel = self.context.socket(zmq.REQ)

        self.cmdchannel.setsockopt(zmq.IDENTITY, self.id)

        # if self.port == 4444 and j.system.platformtype.isLinux():
        #     self.cmdchannel.connect("ipc:///tmp/cmdchannel_clientdaemon")
        #     print "IPC channel opened to client daemon"
        # else:
        self.cmdchannel.connect("tcp://%s:%s" % (self.ipaddr, self.port))
        print "TCP channel opened to %s:%s" % (self.ipaddr, self.port)

        self.poll = zmq.Poller()
        self.poll.register(self.cmdchannel, zmq.POLLIN)

        if self.datachannel:
            port = int(self.sendcmd("getfreeport"))
            if port == 0:
                raise RuntimeError("Could not find free port on clientdaemon")

            self.datachannel = self.context.socket(zmq.PAIR)
            self.datachannel.connect("tcp://localhost:%s" % port)

            print "init port for datachannel: %s" % port

    def sendMsgOverCMDChannel(self, cmd, data, sendformat="m", returnformat="m", retry=1, maxretry=2):
        """
        cmd is command on server (is asci text)
        data is any to be serialized data

        formatstring is right order of formats e.g. mc means messagepack & then compress
        formats see: j.db.serializers.get(?

        return is always multipart message [$resultcode(0=no error,1=autherror),$formatstr,$remainingdata]

        errors are always return using msgpack and are a dict

        """
        rawdata = data
        if sendformat <> "":
            ser = j.db.serializers.get(sendformat, key=self.key)
            data = ser.dumps(data)

        # self.cmdchannel.send_multipart([cmd,sendformat,returnformat,data])
        parts = self.sendMsgOverCMDChannelRetry(cmd, data, sendformat, returnformat)
        returncode = parts[0]

        if returncode in ('1', '3'):
            if retry < maxretry:
                print "session lost"

                if returncode == '3':
                    self.initSession()
                else:
                    self.init()
                retry += 1
                return self.sendMsgOverCMDChannel(cmd, rawdata, sendformat, returnformat, retry, maxretry)
            else:
                msg = "Authentication error on server on %s:%s.\n" % (self.ipaddr, self.port)
                raise RuntimeError(msg)
        elif returncode == '2':
            msg = "execution error on server on %s:%s.\n Could not find method:%s\n" % (self.ipaddr, self.port, cmd)
            j.errorconditationhandler.raiseBug(msgpub=msg, message="", category="rpc.exec")
        elif returncode != "0":
            s = j.db.serializers.getMessagePack()  # get messagepack serializer
            eco = j.errorconditationhandler.getErrorConditionObject(s.loads(parts[2]))
            msg = "execution error on server on %s:%s.\nCmd:%s\nError=%s" % (self.ipaddr, self.port, cmd, eco)
            if cmd == "logeco":
                raise RuntimeError("Could not forward errorcondition object to logserver, error was %s" % eco)
            print "*** error in client to zdaemon ***"
            # print eco
            j.errorconditationhandler.raiseOperationalCritical(msgpub="", message=msg, category="rpc.exec", die=True, tags="ecoguid:%s" % eco.guid)

        returnformat = parts[1]
        if returnformat <> "":
            ser = j.db.serializers.get(returnformat, key=self.key)
            result = ser.loads(parts[2])
        else:
            result = parts[2]

        return result

    def sendMsgOverCMDChannelRetry(self, cmd, data, sendformat="m", returnformat="m"):
        while True:
            # print "Send (%s)" % msg
            self.cmdchannel.send_multipart([cmd, sendformat, returnformat, data])
            expect_reply = True
            while expect_reply:
                socks = dict(self.poll.poll(1000))
                if socks.get(self.cmdchannel) == zmq.POLLIN:
                    reply = self.cmdchannel.recv_multipart()
                    if not reply:
                        break
                    else:
                        return reply
                else:
                    print "W: No response from clientdaemon, retrying"
                    self.reset()
                    self.cmdchannel.send_multipart([cmd, sendformat, returnformat, data])

    def close(self):
        try:
            self.cmdchannel.setsockopt(zmq.LINGER, 0)
            self.cmdchannel.close()
        except:
            print "error in close for cmdchannel"
            pass

        try:
            self.poll.unregister(self.cmdchannel)
        except:
            pass

        try:
            self.datachannel.setsockopt(zmq.LINGER, 0)
            self.datachannel.close()
        except:
            # print "error in close for datachannel"
            pass

        self.context.term()

    def reset(self):
        # Socket is confused. Close and remove it.
        self.close()
        self.init()

    def sendcmd(self, cmd, sendformat="m", returnformat="m", **args):
        """
        formatstring is right order of formats e.g. mc means messagepack & then compress
        formats see: j.db.serializers.get(?

        return is the deserialized data object
        """
        return self.sendMsgOverCMDChannel(cmd, args, sendformat, returnformat)

    def perftest(self):
        start = time.time()
        nr = 10000
        print "start perftest for %s for ping cmd" % nr
        for i in range(nr):
            if not self.sendcmd("ping") == "pong":
                raise RuntimeError("ping did not return pong.")
        stop = time.time()
        nritems = nr / (stop - start)
        print "nr items per sec: %s" % nritems
        print "start perftest for %s for cmd ping" % nr
        for i in range(nr):
            if not self.sendcmd("pingcmd") == "pong":
                raise RuntimeError("ping did not return pong.")
        stop = time.time()
        nritems = nr / (stop - start)
        print "nr items per sec: %s" % nritems


class ZDaemonCmdClient(object):

    def __init__(self, ipaddr="localhost", port=4444, datachannel=False, org="myorg", user="root", passwd="passwd", ssl=False, introspect=True, reset=False, roles=[]):
        self._client = ZDaemonClient(ipaddr, port=port, org=org, user=user, passwd=passwd, ssl=ssl, datachannel=datachannel, reset=reset, roles=roles)

        if introspect:
            self._loadMethods()

    def _loadMethods(self):
        methodspecs = self._client.sendcmd('_introspect')
        for key, spec in methodspecs.iteritems():
            # print "key:%s spec:%s"%(key,spec)
            strmethod = """
class Klass(object):
    def __init__(self, client):
        self._client = client

    def method(%s):
        '''%s'''
        return self._client.sendcmd("%s", "m","m", %s)
"""
            Klass = None
            args = ["%s=%s" % (x, x) for x in spec['args'][0][1:]]
            params_spec = spec['args'][0]
            if spec['args'][3]:
                params_spec = list(spec['args'][0])
                for cnt, default in enumerate(spec['args'][3]):
                    cnt += 1
                    params_spec[-cnt] += "=%r" % default
            params = ', '.join(params_spec)
            strmethod = strmethod % (params, spec['doc'], key, ", ".join(args), )
            exec(strmethod)
            klass = Klass(self._client)
            setattr(self, key, klass.method)
