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

    def authenticate(self,user,passwd,**args):
        return True #will authenticall all (is std)

    def registerpubkey(self,organization,user,pubkey,**args):
        from IPython import embed
        print "DEBUG NOW register pubkeyr"
        embed()

    def getpubkeyserver(self,**args):
        return self.daemon.keystor.getPubKey(self.daemon.sslorg,self.daemon.ssluser,True)

    def registersession(self,sessiondata,**args):
        from IPython import embed
        print "DEBUG NOW sessiondata111"
        embed()

    def logeco(self, eco,**args):
        """
        log eco object (as dict)
        """
        eco["epoch"]=self.daemon.now
        eco=o.errorconditionhandler.getErrorConditionObject(ddict=eco)
        self.daemon.eventhandlingTE.executeV2(eco=eco,history=self.daemon.eventsMemLog)

    def pingcmd(self,**args):
        return "pong"

    def _introspect(self,**args):
        methods = {}
        for name, method in inspect.getmembers(self, inspect.ismethod):
            if name.startswith('_'):
                continue
            args = inspect.getargspec(method)
            methods[name] = {'args' : args, 'doc': inspect.getdoc(method)}
        return methods

