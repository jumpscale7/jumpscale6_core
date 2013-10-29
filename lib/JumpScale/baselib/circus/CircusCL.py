from JumpScale import j
import circus
from circus import commands
from circus.client import CircusClient
import types

class CircusCL():

    def __init__(self):
        self.client=CircusClient()
        self._cmds={}
        self.getCommands()

    def getCommands(self):
        cmds=commands.get_commands()
        result={}

        self._code=""
        for key in cmds.keys():
            cmd=cmds[key]            
            self._cmds[key]=cmd
            result[key]=cmd.properties
            args=""
            args2=""
            args3=""
            for prop in cmd.properties:
                args+="%s=\"\","%(prop)                
                args2+="%s,"%(prop)
                args3+="%s=%s,"%(prop,prop)
            args=args.strip(",")
            args2=args2.strip(",")
            if args<>"":
                args=",%s"%args
            args3=args3.strip(",")
            code="def %s(self%s):\n"%(key,args)
            code+="    cmd=self._cmds[\"%s\"]\n"%key
            code+="    msg=cmd.make_message(%s)\n"%args3
            # code+="    print msg\n"
            code+="    return self.client.call(msg)\n"

            code+="self.%s=types.MethodType( %s, self )\n"%(key,key)

            exec(code)

            self._code+=code+"\n"
            
        return result

    def listWatchers(self):
        result=self.client.call({'command': 'list', 'properties': {}})
        return result["watchers"]

    def startWatcher(self, watchername):
        result = self.client.call({"command":"start", "properties": {"name": watchername}})
        return result

    def stopWatcher(self, watchername):
        result = self.client.call({"command":"stop", "properties": {"name": watchername}})
        return result

    def restartWatcher(self, watchername):
        result = self.client.call({"command":"restart", "properties": {"name": watchername}})
        return result

    def reloadWatcher(self, watchername):
        result = self.client.call({"command":"reload", "properties": {"name": watchername, "graceful": True, "waiting": False}})
        return result








