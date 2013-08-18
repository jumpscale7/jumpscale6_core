from OpenWizzy import o
import OpenWizzy.baselib.serializers
import inspect
import time

class Session():
    def __init__(self,ddict):
        self.__dict__=ddict

    def __repr__(self):
        return str(self.__dict__)

    __str__=__repr__        


class DaemonCMDS(object):
    def __init__(self, daemon):
        self.daemon = daemon

    def authenticate(self,session):
        return True #will authenticall all (is std)

    def registerpubkey(self,organization,user,pubkey,session):
        self.daemon.keystor.setPubKey(organization, user, pubkey)
        return ""

    def getpubkeyserver(self,session):
        return self.daemon.keystor.getPubKey(self.daemon.sslorg,self.daemon.ssluser,returnAsString=True)

    def registersession(self,data,session,ssl):
        """
        @param sessiondata is encrypted data (SSL)
        """
        ser=o.db.serializers.getMessagePack()
        sessiondictstr=ser.loads(data)

        session=Session(sessiondictstr)

        #@todo JO fix ssl please
        ssl=False
        if ssl:
            session.encrkey=self.daemon.keystor.decrypt(orgsender=session.organization, sender=session.user, \
                orgreader=self.daemon.sslorg,reader=self.daemon.ssluser, \
                message=session.encrkey[0], signature=session.encrkey[1])

            session.passwd=self.daemon.keystor.decrypt(orgsender=session.organization, sender=session.user, \
                orgreader=self.daemon.sslorg,reader=self.daemon.ssluser, \
                message=session.passwd[0], signature=session.passwd[1])

        if not self.authenticate(session):
            raise RuntimeError("Cannot Authenticate User:%s"%session.user)

        self.daemon.sessions[session.id]=session

        return "OK"

    def logeco(self, eco,session):
        """
        log eco object (as dict)
        """
        eco["epoch"]=self.daemon.now
        eco=o.errorconditionhandler.getErrorConditionObject(ddict=eco)
        self.daemon.eventhandlingTE.executeV2(eco=eco,history=self.daemon.eventsMemLog)


class Daemon(object):

    def __init__(self,name=None):

        self.name=name
        self.cmds = {}

        self.cmdsInterfaces = {}

        self._now=0

        self.sessions={}

        self.key=""

        self.errorconditionserializer=o.db.serializers.getSerializerType("j")

        self.addCMDsInterface(DaemonCMDS,"core")

    def getTime(self):
        #can overrule this to e.g. in gevent set the time every sec, takes less resource (using self._now)
        return int(time.time())

    def introspect(self,cmds,category=""):
        methods = {}
        for name, method in inspect.getmembers(cmds, inspect.ismethod):
            if name.startswith('_'):
                continue
            args = inspect.getargspec(method)
            #Remove the 'session' parameter
            if 'session' in args.args:
                session_index = args.args.index('session')
                del args.args[session_index]
                if args.defaults:
                    session_default_index = session_index - len(args.args) -1
                    defaults = list(args.defaults)
                    del defaults[session_default_index]
                    args = inspect.ArgSpec(args.args, args.varargs, args.keywords, defaults)

            methods[name] = {'args' : args, 'doc': inspect.getdoc(method)}
        return methods


    def addCMDsInterface(self, cmdInterfaceClass,category=""):
        if not self.cmdsInterfaces.has_key(category):
            self.cmdsInterfaces[category]=[]
        self.cmdsInterfaces[category].append(cmdInterfaceClass(self))

    def setCMDsInterface(self, cmdInterfaceClass,category=""):
        self.cmdsInterfaces[category]=[]
        self.cmdsInterfaces[category].append(cmdInterfaceClass(self))

    def processRPC(self, cmd,data,returnformat,session,category=""):
        """
        list with item 0=cmd, item 1=args (dict)

        @return (resultcode,returnformat,result)
        resultcode
            0=ok
            1= not authenticated
            2= method not found
            2+ any other error
        """
        inputisdict=isinstance(data, dict)

        # print "process rpc:\n%s"%data
        cmdkey="%s_%s"%(category,cmd)
        # cmd2 = {}
        if cmdkey in self.cmds:
            ffunction = self.cmds[cmdkey]
        else:
            ffunction = None

            for cmdinterface in self.cmdsInterfaces[category]:
                if hasattr(cmdinterface,cmd):
                    ffunction = getattr(cmdinterface, cmd)

            if ffunction == None:
                #means could not find method
                return "2","",None

            self.cmds[cmdkey] = ffunction

        takessession = 'session' in inspect.getargspec(ffunction).args
        try:
            if inputisdict:          
                if takessession:
                    data['session'] = session
                result = ffunction(**data)
            else:
                if takessession:
                    result = ffunction(data,session=session)
                else:
                    result = ffunction(data)
        except Exception, e:
            eco=o.errorconditionhandler.parsePythonErrorObject(e)
            eco.level=2
            print eco
            o.errorconditionhandler.processErrorConditionObject(eco)            
            return "3","",self.errorconditionserializer.dumps(eco.__dict__)

        return "0",returnformat,result


    def processRPCUnSerialized(self,cmd,informat,returnformat,data,sessionid,category=""):

        if self.sessions.has_key(sessionid):
            session=self.sessions[sessionid]
        else:
            if cmd in ["registerpubkey","getpubkeyserver","registersession"]:
                session=None
                returnformat=""
                category="core"
            else:
                error = "Authentication  or Session error, session not known with id:%s"%sessionid
                eco = o.errorconditionhandler.getErrorConditionObject(msg=error)
                return "3","", self.errorconditionserializer.dumps(eco.__dict__)

        if informat<>"":
            ser=o.db.serializers.get(informat,key=self.key)
            data=ser.loads(data)                

        parts = self.processRPC(cmd,data,returnformat=returnformat,session=session,category=category)
        returnformat=parts[1] #return format as comes back from processRPC
        if returnformat<>"": #is 
            returnser = o.db.serializers.get(returnformat,key=session.encrkey)
            data=returnser.dumps(parts[2])
        else:
            data=parts[2]

        if data==None:
            data=""

        return (parts[0],parts[1],data)

