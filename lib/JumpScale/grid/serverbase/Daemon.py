from JumpScale import j
import JumpScale.baselib.serializers
from JumpScale.grid.serverbase import returnCodes
from JumpScale.core.errorhandling.ErrorConditionHandler import BaseException
import inspect
import copy
import time
import ujson


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

    def registersession(self, sessiondata, ssl,session):
        """
        @param sessiondata is encrypted data (SSL)
        """
        # ser=j.db.serializers.getMessagePack()
        # sessiondictstr=ser.loads(data)
        print "register session:%s "%session
        session = Session(sessiondata)

        if ssl:
            session.encrkey = self.daemon.decrypt(session.encrkey, session)
            session.passwd = self.daemon.decrypt(session.passwd, session)

        if not self.authenticate(session):
            raise RuntimeError("Cannot Authenticate User:%s" % session.user)

        self.daemon.sessions[session.id] = session
        print "OK"

        return "OK"

    def logeco(self, eco, session):
        """
        log eco object (as dict)
        """
        eco["epoch"] = self.daemon.now
        eco = j.errorconditionhandler.getErrorConditionObject(ddict=eco)
        self.daemon.eventhandlingTE.executeV2(eco=eco, history=self.daemon.eventsMemLog)

    def introspect(self, cat,session=None):
        methods = {}
        interface = self.daemon.cmdsInterfaces[cat]
        for name, method in inspect.getmembers(interface, inspect.ismethod):
            if name.startswith('_'):
                continue
            args = inspect.getargspec(method)
            # Remove the 'session' parameter
            if 'session' in args.args:
                session_index = args.args.index('session')
                if session_index<>len(args.args)-1:
                    raise RuntimeError("session arg needs to be last argument of method. Cat:%s Method:%s \nArgs:%s"%(cat,name,args))
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
        j.application.shellconfig.interactive = False # make sure errorhandler does not require input we are daemon
        self.name = name
        self.cmds = {}
        self.cmdsInterfaces = {}
        self.cmdsInterfacesProxy = {}
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

    def addCMDsInterface(self, cmdInterfaceClass, category,proxy=False):
        if not self.cmdsInterfaces.has_key(category):
            self.cmdsInterfaces[category] = []
        if proxy==False:
            obj=cmdInterfaceClass(self)
        else:
            obj=cmdInterfaceClass()
            self.cmdsInterfacesProxy[category]=obj
        self.cmdsInterfaces[category]=obj

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
            if not self.cmdsInterfaces.has_key(category):
                return returnCodes.METHOD_NOT_FOUND, "", None

            cmdinterface= self.cmdsInterfaces[category]
            if hasattr(cmdinterface, cmd):
                ffunction = getattr(cmdinterface, cmd)
            else:
                return returnCodes.METHOD_NOT_FOUND, "", None

            self.cmds[cmdkey] = ffunction

        try:
            if inputisdict:
                if data.has_key("_agentid"):
                    if data["_agentid"]<>0:
                        cmds=self.cmdsInterfaces["agent"]
                        gid=j.application.whoAmI.gid
                        nid=int(data["_agentid"])
                        data.pop("_agentid")
                        category2=category.replace("processmanager_","")
                        scriptid="%s_%s" % (category2, cmd)
                        job=cmds.scheduleCmd(gid,nid,cmdcategory=category2,jscriptid=scriptid,cmdname=cmd,args=data,queue="internal",log=False,timeout=60,roles=[],session=session,wait=True)
                        jobqueue = cmds._getJobQueue(job["guid"])
                        jobr=jobqueue.get(True,60)
                        if not jobr:
                            eco = j.errorconditionhandler.getErrorConditionObject(msg="Command %s.%s with args: %s timeout" % (category2, cmd, data))
                            return returnCodes.ERROR,returnformat,eco.__dict__
                        jobr=ujson.loads(jobr)
                        if jobr["state"]<>"OK":
                            return jobr["resultcode"],returnformat,jobr["result"]
                        else:
                            return returnCodes.OK,returnformat,jobr["result"]
                    else:
                        data['session'] = session
                        data.pop("_agentid")
                result = ffunction(**data)
            else:
                result = ffunction(data, session=session)
        except Exception, e:
            # if str(e)=="STOP APPLICATION 112299":  #needs to be cryptic otherwise smart developers can fake this
            #     j.application.stop()
            if isinstance(e, BaseException):
                return returnCodes.ERROR, returnformat, e.eco
            eco = j.errorconditionhandler.parsePythonErrorObject(e)
            eco.level = 2
            # print eco
            # eco.errormessage += "\nfunction arguments were:%s\n" % str(inspect.getargspec(ffunction).args)
            if len(str(data))>1024:
                msg="too much data to show."
            else:
                data2 = data.copy()
                data2.pop('session', None)
                msg = ujson.dumps(data)

            if session:
                nid = session.nid
                gid = session.gid
            else:
                nid = 0
                gid = 0
            
            eco.errormessage = "ERROR IN RPC CALL %s: %s. (from:%s/%s)\nData:%s\n"%(cmdkey,eco.errormessage, gid, nid,msg)
            eco.process()
            eco.__dict__.pop("tb", None)
            eco.tb=None
            errorres = eco.__dict__
            return returnCodes.ERROR, returnformat, errorres 

        return returnCodes.OK, returnformat, result

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
                return returnCodes.AUTHERROR, "m", self.errorconditionserializer.dumps(eco.__dict__)
        try:
            if informat <> "":
                ser = j.db.serializers.get(informat, key=self.key)
                data = ser.loads(data)
        except Exception,e:
            eco=j.errorconditionhandler.parsePythonErrorObject(e)
            eco.tb=""
            return returnCodes.SERIALIZATIONERRORIN, "m", self.errorconditionserializer.dumps(eco.__dict__)


        parts = self.processRPC(cmd, data, returnformat=returnformat, session=session, category=category)
        returnformat = parts[1]  # return format as comes back from processRPC
        if returnformat <> "":  # is
            returnser = j.db.serializers.get(returnformat, key=encrkey)
            error=0
            try:
                data = self.encrypt(returnser.dumps(parts[2]), session)
            except Exception,e:
                error=1
            if error==1:
                try:
                    data = self.encrypt(returnser.dumps(parts[2].__dict__), session)
                except:
                    eco = j.errorconditionhandler.getErrorConditionObject(msg="could not serialize result from %s"%cmd)
                    return returnCodes.SERIALIZATIONERROROUT, "m", self.errorconditionserializer.dumps(eco.__dict__)
        else:
            data = parts[2]

        if data == None:
            data = ""

        return (parts[0], parts[1], data)
