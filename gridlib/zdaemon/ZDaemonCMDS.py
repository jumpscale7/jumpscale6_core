from OpenWizzy import o
import inspect

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

    def registerpubkey(self,organization,user,pubkey,**args):
        from IPython import embed
        print "DEBUG NOW register pubkeyr"
        embed()

    def getpubkeyserver(self,session):
        return self.daemon.keystor.getPubKey(self.daemon.sslorg,self.daemon.ssluser,True)

    def registersession(self,organization,user,macaddr,hostname,session):
        """
        @param sessiondata is encrypted data (SSL)
        """
        from IPython import embed
        print "DEBUG NOW sessiondata111"
        embed()

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
            methods[name] = {'args' : args, 'doc': inspect.getdoc(method)}
        return methods

