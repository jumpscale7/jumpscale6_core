from OpenWizzy import o
import inspect

class Session():
    def __init__(self,ddict):
        self.__dict__=ddict

    def __repr__(self):
        return str(self.__dict__)

    __str__=__repr__        


class ZDaemonCMDS(object):
    def __init__(self, daemon):
        self.daemon = daemon

    # def getfreeport(self):
    #     """
    #     init a datachannelProcessor on found port
    #     is a server in pair socket processing incoming data
    #     each scheduled instance is on separate port
    #     """
    #     return self.daemon.getfreeportAndSchedule("datachannelProcessor", self.daemon.datachannelProcessor)


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

    def pingcmd(self,session):
        return "pong"

    def _introspect(self,session):
        methods = {}
        for name, method in inspect.getmembers(self, inspect.ismethod):
            if name.startswith('_'):
                continue
            args = inspect.getargspec(method)
            if 'session' in args.args:
                args.args.remove("session")
            methods[name] = {'args' : args, 'doc': inspect.getdoc(method)}
        return methods

