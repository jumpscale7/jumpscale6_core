from JumpScale import j
import JumpScale.portal

class system_master(j.code.classGetBase()):

    """
    get dict of list of apps & actors
    
    """

    def __init__(self):

        self._te = {}
        self.actorname = "master"
        self.appname = "system"

    def echo(self, input, **args):
        """
        just a simple echo service
        param:input result will be same as this input
        result str 
        
        """
        return input

    def getAppsActors(self, model, **args):
        """
        param:model if you want to also get model actors; otherwise 0
        result dict 
        
        """
        if int(model) == 1:
            result = j.core.specparser.app_actornames
        else:
            result = {}
            for app in j.core.specparser.app_actornames.keys():
                result[app] = []
                actors = j.core.specparser.app_actornames[app]
                for actor in actors:
                    if actor.find("_model_") == -1:
                        result[app].append(actor)

        return result

    def ping(self, **args):
        """
        just a simple ping to the service        
        """
        return "pong"

    def registerRedisInstance(self, ipaddr, port, secret, appname, actorname, **args):
        """
        get dict of list of apps & actors
        param:ipaddr ipaddr of instance
        param:port port
        param:secret secret
        param:appname appname
        param:actorname actorname
        result dict 
        
        """
        # put your code here to implement this method
        raise NotImplementedError("not implemented method registerRedisInstance")

    def waitForJob(self, jobid, timeout=10, **args):
        jobid = int(jobid)
        if jobid not in j.core.portal.runningPortal.webserver.jobids2greenlets:
            j.core.portal.runningPortal.webserver.spawnJob(jobid)
        result = j.core.portal.runningPortal.webserver.jobids2greenlets[jobid].get(timeout=timeout)
        if result:
            j.core.portal.runningPortal.webserver.jobids2greenlets.pop(jobid)
            return j.db.serializers.getSerializerType('j').loads(result)
        else:
            return None
