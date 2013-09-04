from JumpScale import j
import JumpScale.baselib.serializers
import inspect
import time


class Session():

    def __init__(self, ddict):
        self.__dict__ = ddict

    def __repr__(self):
        return str(self.__dict__)

    __str__ = __repr__


class DaemonCMDS(object):

    def __init__(self, daemon):
        self.daemon = daemon

    def authenticate(self, session):
        return True  # will authenticall all (is std)

    def registerpubkey(self, organization, user, pubkey, session):
        self.daemon.keystor.setPubKey(organization, user, pubkey)
        return ""

    def listCategories(self, session):
        return self.daemon.cmdsInterfaces.keys()

    def getpubkeyserver(self, session):
        return self.daemon.keystor.getPubKey(self.daemon.sslorg, self.daemon.ssluser, returnAsString=True)

    def registersession(self, sessiondata, session, ssl):
        """
        @param sessiondata is encrypted data (SSL)
        """
        # ser=j.db.serializers.getMessagePack()
        # sessiondictstr=ser.loads(data)

        session = Session(sessiondata)

        if ssl:
            session.encrkey = self.daemon.decrypt(session.encrkey, session)
            session.passwd = self.daemon.decrypt(session.passwd, session)

        if not self.authenticate(session):
            raise RuntimeError("Cannot Authenticate User:%s" % session.user)

        self.daemon.sessions[session.id] = session

        return "OK"

    def logeco(self, eco, session):
        """
        log eco object (as dict)
        """
        eco["epoch"] = self.daemon.now
        eco = j.errorconditionhandler.getErrorConditionObject(ddict=eco)
        self.daemon.eventhandlingTE.executeV2(eco=eco, history=self.daemon.eventsMemLog)

    def introspect(self, session, cat):
        methods = {}
        interfaces = self.daemon.cmdsInterfaces[cat]
        for interface in interfaces:
            for name, method in inspect.getmembers(interface, inspect.ismethod):
                if name.startswith('_'):
                    continue
                args = inspect.getargspec(method)
                # Remove the 'session' parameter
                if 'session' in args.args:
                    session_index = args.args.index('session')
                    del args.args[session_index]
                    if args.defaults:
                        session_default_index = session_index - len(args.args) - 1
                        defaults = list(args.defaults)
                        del defaults[session_default_index]
                        args = inspect.ArgSpec(args.args, args.varargs, args.keywords, defaults)

                methods[name] = {'args': args, 'doc': inspect.getdoc(method)}
        return methods


class Daemon(object):

    def __init__(self, name=None):

        self.name = name
        self.cmds = {}

        self.cmdsInterfaces = {}

        self._now = 0

        self.sessions = {}

        self.key = ""

        self.errorconditionserializer = j.db.serializers.getSerializerType("m")

        self.addCMDsInterface(DaemonCMDS, "core")

    def getTime(self):
        # can overrule this to e.g. in gevent set the time every sec, takes less resource (using self._now)
        return int(time.time())

    def decrypt(self, message, session):
        if session.encrkey:
            return self.keystor.decrypt(orgsender=session.organization, sender=session.user,
                                        orgreader=self.sslorg, reader=self.ssluser,
                                        message=message[0], signature=message[1])
        else:
            return message

    def encrypt(self, message, session):
        if session and session.encrkey:
            if not hasattr(session, 'publickey'):
                session.publickey = self.keystor.getPubKey(user=session.user, organization=session.organization, returnAsString=True)
            return self.keystor.encrypt(self.sslorg, self.ssluser, "", "", message, False, pubkeyReader=session.publickey)[0]
        else:
            return message

    def addCMDsInterface(self, cmdInterfaceClass, category=""):
        if not self.cmdsInterfaces.has_key(category):
            self.cmdsInterfaces[category] = []
        self.cmdsInterfaces[category].append(cmdInterfaceClass(self))

    def setCMDsInterface(self, cmdInterfaceClass, category=""):
        self.cmdsInterfaces[category] = []
        self.cmdsInterfaces[category].append(cmdInterfaceClass(self))

    def processRPC(self, cmd, data, returnformat, session, category=""):
        """

        @return (resultcode,returnformat,result)
                item 0=cmd, item 1=returnformat (str), item 2=args (dict)
        resultcode
            0=ok
            1= not authenticated
            2= method not found
            2+ any other error
        """
        inputisdict = isinstance(data, dict)

        # print "process rpc:\n%s"%data
        cmdkey = "%s_%s" % (category, cmd)
        # cmd2 = {}
        if cmdkey in self.cmds:
            ffunction = self.cmds[cmdkey]
        else:
            ffunction = None

            for cmdinterface in self.cmdsInterfaces[category]:
                if hasattr(cmdinterface, cmd):
                    ffunction = getattr(cmdinterface, cmd)

            if ffunction == None:
                # means could not find method
                return "2", "", None

            self.cmds[cmdkey] = ffunction

        # takessession = 'session' in inspect.getargspec(ffunction).args
        # DO NOT DO THIS THIS IS SLOW !
        try:
            if inputisdict:
                data['session'] = session
                result = ffunction(**data)
            else:
                result = ffunction(data, session=session)
        except Exception, e:
            eco = j.errorconditionhandler.parsePythonErrorObject(e)
            eco.level = 2
            # print eco
            eco.errormessage += "\nfunction arguments were:%s\n" % str(inspect.getargspec(ffunction).args)
            j.errorconditionhandler.processErrorConditionObject(eco)
            result = self.errorconditionserializer.dumps(eco.__dict__)
            return "3", "", result

        return "0", returnformat, result

    def processRPCUnSerialized(self, cmd, informat, returnformat, data, sessionid, category=""):
        """
        @return (resultcode,returnformat,result)
                item 0=cmd, item 1=returnformat (str), item 2=args (dict)
        resultcode
            0=ok
            1= not authenticated
            2= method not found
            2+ any other error
        """
        if self.sessions.has_key(sessionid):
            session = self.sessions[sessionid]
            encrkey = session.encrkey
        else:
            if cmd in ["registerpubkey", "getpubkeyserver", "registersession"]:
                session = None
                encrkey = ""
            else:
                error = "Authentication  or Session error, session not known with id:%s" % sessionid
                eco = j.errorconditionhandler.getErrorConditionObject(msg=error)
                return "3", "", self.errorconditionserializer.dumps(eco.__dict__)

        if informat <> "":
            ser = j.db.serializers.get(informat, key=self.key)
            data = ser.loads(data)

        parts = self.processRPC(cmd, data, returnformat=returnformat, session=session, category=category)
        returnformat = parts[1]  # return format as comes back from processRPC
        if returnformat <> "":  # is
            returnser = j.db.serializers.get(returnformat, key=encrkey)
            data = self.encrypt(returnser.dumps(parts[2]), session)
        else:
            data = parts[2]

        if data == None:
            data = ""

        return (parts[0], parts[1], data)
