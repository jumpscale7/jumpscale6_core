from JumpScale import j
import JumpScale.baselib.serializers
from JumpScale.grid.serverbase.Exceptions import AuthenticationError, MethodNotFoundException
from JumpScale.grid.serverbase import returnCodes
import time
import struct
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
        self.agentid="%s_%s_%s"%(j.application.whoAmI.gid,j.application.whoAmI.bid,j.application.whoAmI.nid)

    def __repr__(self):
        return str(self.__dict__)

    __str__ = __repr__


class SimpleClient(object):
    def __init__(self, client):
        self._client = client


class DaemonClient(object):

    def __init__(self, org="myorg", user="root", passwd="passwd", ssl=False, encrkey="", reset=False, roles=[], \
        transport=None, defaultSerialization="m",id=None):
        """
        @param encrkey (use for simple blowfish shared key encryption, better to use SSL though, will do the same but dynamically exchange the keys)
        """
        if id<>None:
            self._id=id
        else:
            end = 4294967295  # 4bytes max nr
            self._id = struct.pack("<III", j.base.idgenerator.generateRandomInt(
                1, end), j.base.idgenerator.generateRandomInt(1, end), j.base.idgenerator.generateRandomInt(1, end))

        self.retry = True
        self.blocksize = 8 * 1024 * 1024
        self.key = encrkey
        self.user = user
        self.org = org
        self.passwd = passwd
        self.ssl = ssl
        # if roles==[]:
        #     roles=j.application.config.get("node.roles").split(",")
        #     roles=[item.strip().lower() for item in roles]

        self.roles = roles
        self.keystor = None
        self.key = None
        self.transport = transport
        self.pubkeyserver = None
        self.defaultSerialization = defaultSerialization
        self.transport.connect(self._id)
        self.initSession(reset, ssl)

    def encrypt(self, message):
        if self.ssl:
            if not self.pubkeyserver:
                self.pubkeyserver = self.sendcmd(category="core", cmd="getpubkeyserver")
            return self.keystor.encrypt(self.org, self.user, "", "", message=message, sign=True, base64=True, pubkeyReader=self.pubkeyserver)
        return message

    def decrypt(self, message):
        if self.ssl and self.key:
            return self.keystor.decrypt("", "", self.org, self.user, message)
        else:
            return message

    def initSession(self, reset=False, ssl=False):

        if ssl:
            from JumpScale.baselib.ssl.SSL import SSL
            self.keystor = SSL().getSSLHandler()
            try:
                publickey = self.keystor.getPubKey(self.org, self.user, returnAsString=True)
            except:
                # priv key now known yet
                reset = True

            if reset:
                publickey, _ = self.keystor.createKeyPair(organization=self.org, user=self.user)

            self.sendcmd(category="core", cmd="registerpubkey", organization=self.org, user=self.user, pubkey=publickey)

            # generate unique key
            encrkey = ""
            for i in range(56):
                encrkey += chr(randrange(0, 256))

            # only encrypt the key & the passwd, the rest is not needed
            encrkey = self.encrypt(encrkey)
            passwd = self.encrypt(self.passwd)

        else:
            encrkey = ""
            publickey = ""
            passwd = self.passwd

        session = Session(id=self._id, organization=self.org, user=self.user, passwd=passwd,
                          encrkey=encrkey, netinfo=j.system.net.getNetworkInfo(), roles=self.roles)
        # ser=j.db.serializers.getMessagePack()
        # sessiondictstr=ser.dumps(session.__dict__)
        self.key = session.encrkey
        self.sendcmd(category="core", cmd="registersession", sessiondata=session.__dict__, ssl=ssl, returnformat="")

    def sendMsgOverCMDChannel(self, cmd, data, sendformat=None, returnformat=None, retry=0, maxretry=1, category=None,die=False):
        """
        cmd is command on server (is asci text)
        data is any to be serialized data

        formatstring is right order of formats e.g. mc means messagepack & then compress
        formats see: j.db.serializers.get(?

        return is always multipart message [$resultcode(0=no error,1=autherror),$formatstr,$remainingdata]

        errors are always return using msgpack and are a dict

        """
        if sendformat == None:
            sendformat = self.defaultSerialization
        if returnformat == None:
            returnformat = self.defaultSerialization

        rawdata = data
        if sendformat <> "":
            ser = j.db.serializers.get(sendformat, key=self.key)
            data = ser.dumps(data)

        # self.cmdchannel.send_multipart([cmd,sendformat,returnformat,data])
        parts = self.transport.sendMsg(category, cmd, data, sendformat, returnformat)
        returncode = parts[0]

        if returncode == returnCodes.AUTHERROR:
            if retry < maxretry:
                print "session lost"

                self.initSession()
                retry += 1
                return self.sendMsgOverCMDChannel(cmd, rawdata, sendformat, returnformat, retry, maxretry, category)
            else:
                msg = "Authentication error on server.\n"
                raise AuthenticationError(msg)
        elif returncode == returnCodes.METHOD_NOT_FOUND:
            msg = "Execution error on %s.\n Could not find method:%s\n" % (self.transport, cmd)
            raise MethodNotFoundException(msg)
        if str(returncode) != returnCodes.OK:
            s = j.db.serializers.getMessagePack()  # get messagepack serializer
            ddict = s.loads(parts[2])
            eco = j.errorconditionhandler.getErrorConditionObject(ddict)
            msg = "execution error on server cmd:%s error=%s" % (cmd, eco)
            if cmd == "logeco":
                raise RuntimeError("Could not forward errorcondition object to logserver, error was %s" % eco)
            print "*** error in client to zdaemon ***"
            # print eco
            j.errorconditionhandler.raiseOperationalCritical(msgpub="", message=msg, category="rpc.exec", die=die, tags="ecoguid:%s" % eco.guid)
            raise RuntimeError(str(eco))

        returnformat = parts[1]
        if returnformat <> "":
            ser = j.db.serializers.get(returnformat, key=self.key)
            res = self.decrypt(parts[2])
            result = ser.loads(res)
        else:
            result = parts[2]

        return result

    def reset(self):
        # Socket is confused. Close and remove it.
        self.transport.close()
        self.transport.connect(self._id)


    def getCmdClient(self, category,sendformat="m", returnformat="m"):
        if category == "*":
            categories = self.sendcmd(category='core', cmd='listCategories')
            cl = SimpleClient(self)
            for category in categories:
                setattr(cl, category, self._getCmdClient(category))
            return cl
        else:
            return self._getCmdClient(category,sendformat,returnformat)


    def _getCmdClient(self, category,sendformat="m", returnformat="m"):
        client = SimpleClient(self)
        methodspecs = self.sendcmd(category='core', cmd='introspect', cat=category)
        for key, spec in methodspecs.iteritems():
            # print "key:%s spec:%s"%(key,spec)
            strmethod = """
class Klass(object):
    def __init__(self, client, category):
        self._client = client
        self._category = category

    def method(%s):
        '''%s'''
        return self._client.sendcmd(cmd="%s", category=self._category, %s,sendformat="${sendformat}",returnformat="${returnformat}")
"""
            strmethod=strmethod.replace("${sendformat}",sendformat)
            strmethod=strmethod.replace("${returnformat}",returnformat)
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
            try:
                exec(strmethod)
            except Exception,e:
                raise RuntimeError("could not exec the client method, error:%s, code was:%s"%(e,strmethod))
            klass = Klass(self, category)
            setattr(client, key, klass.method)
        return client

    def sendcmd(self, cmd, sendformat=None, returnformat=None, category=None, **args):
        """
        formatstring is right order of formats e.g. mc means messagepack & then compress
        formats see: j.db.serializers.get(?

        return is the deserialized data object
        """
        return self.sendMsgOverCMDChannel(cmd, args, sendformat, returnformat, category=category)

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




class Transport(object):

    def connect(self, sessionid=None):
        """
        everwrite this method in implementation to init your connection to server (the transport layer)
        """
        raise RuntimeError("not implemented")

    def close(self):
        """
        close the connection (reset all required)
        """
        raise RuntimeError("not implemented")

    def sendMsg(self, category, cmd, data, sendformat="m", returnformat="m"):
        """
        overwrite this class in implementation to send & retrieve info from the server (implement the transport layer)

        @return (resultcode,returnformat,result)
                item 0=cmd, item 1=returnformat (str), item 2=args (dict)
        resultcode
            0=ok
            1= not authenticated
            2= method not found
            2+ any other error
        """
        raise RuntimeError("not implemented")
        # send message, retry if needed, retrieve message


