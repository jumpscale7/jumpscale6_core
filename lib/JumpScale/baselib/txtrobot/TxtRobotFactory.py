from JumpScale import j
import yaml
import hashlib
from TxtRobotHelp import TxtRobotHelp
from TxtRobotSnippet import TxtRobotSnippet
import JumpScale.baselib.redis

class TxtRobotFactory(object):

    def __init__(self):
        pass
        
    def get(self, definition):
        """
        example definition:
        
        project (proj,p)
        - list (l)
        - delete (del,d)
        -- name (n)
        user (u)
        - list (l)
        """
        return TxtRobot(definition)

class TxtRobot():
    def __init__(self,definition):
        self.definition=definition.replace('\n', '<br/>')
        self.cmdAlias={}
        self.entityAlias={}
        self.entities=[]
        self.cmds={}
        self._initCmds(definition)
        self.cmdsToImpl={}
        self.help=TxtRobotHelp()
        self.snippet = TxtRobotSnippet()
        self.cmdobj=None
        self.redis=j.clients.redis.getRedisClient("localhost",7768)

    def _initCmds(self,definition):
        for line in definition.split("\n"):
            # print line
            line=line.strip()
            if line=="":
                continue
            if line[0]=="#":
                continue

            if line.find("###")<>-1:
                break

            if line[0]<>"-":
                if line.find(" ")<>-1:
                    ent,remainder=line.split(" ",1)
                else:
                    ent=line
                    remainder=""
                ent=ent.lower().strip()
                self.entities.append(ent)
                if remainder.find("(")<>-1 and remainder.find(")")<>-1:
                    r=remainder.strip("(")
                    r=r.strip(")")
                    r=r.strip()
                    for alias in r.split(","):
                        alias=alias.lower().strip()
                        self.entityAlias[alias]=ent

            if line[0]=="-" and line[1]<>"-":
                if ent=="":
                    raise RuntimeError("entity cannot be '', line:%s"%line)
                line=line.strip("-")
                line=line.strip()
                if line.find(" ")==-1:
                    cmd=line
                    remainder=""
                else:
                    cmd,remainder=line.split(" ",1)
                cmd=cmd.lower().strip()
                if not self.cmds.has_key(ent):
                    self.cmds[ent]=[]
                if not self.cmdAlias.has_key(ent):
                    self.cmdAlias[ent]={}
                if cmd not in self.cmds[ent]:
                    self.cmds[ent].append(cmd)

                if remainder.find("(")<>-1 and remainder.find(")")<>-1:
                    r=remainder.strip("(")
                    r=r.strip(")")
                    r=r.strip()
                    for alias in r.split(","):
                        alias=alias.lower().strip()
                        self.cmdAlias[ent][alias]=cmd                

    def error(self,msg,help=False):
        if help:
            msg="%s\n%s\n"%(msg,self.help.intro())
        msg="*****ERROR*******\n%s"%msg
        print msg
        j.application.stop()

    def findGlobalArgs(self,txt):
        
        alias={}
        alias["l"]="login"
        alias["p"]="passwd"
        alias["pwd"]="passwd"
        alias["password"]="passwd"
        res={}
        out=""
        body=False
        for line in txt.split("\n"):
            if line.strip()=="":
                continue
            if line[0]=="#":
                continue
            if line[0]=="!":
                body=True
            if line.find("=")<>-1 and body==False:
                name,data=line.split("=",1)
                name=name.lower()
                if alias.has_key(name):
                    name=alias[name]
                res[name]=data.strip()
                continue
            out+="%s\n"%line
        
        return out,res

    def _longTextTo1Line(self,txt):
        state="start"
        out=""
        lt=""
        ltstart=""
        for line in txt.split("\n"):
            line=line.strip()
            if state=="LT":
                if len(line)>0 and line.find("...")==0:
                    #means we reached end of block
                    state="start"
                    out+="%s%s\n"%(ltstart,lt)
                    ltstart=""
                    lt=""
                else:
                    lt+="%s\\n"%line
                    continue      
            if len(line)>0 and line[0]=="#":
                continue      
            if state=="start" and line.find("=")<>-1:
                before,after=line.split("=",1)                
                if after.strip()[0:3]=="...":
                    state="LT"
                    ltstart="%s="%before
                    continue

            out+="%s\n"%line
            
        return out        

    def process(self,txt):
        txt=self._longTextTo1Line(txt)
        txt,gargs=self.findGlobalArgs(txt)
        entity=""
        args={}
        cmd=""
        out=""
        
        for line in txt.split("\n"):
            # print "process:%s"%line
            line=line.strip()
            if line=="":
                continue
            if line[0]=="#":
                continue            
            if line=="?" or line=="h" or line=="help":
                return self.help.help()
            if line.find("help.definition")<>-1:
                out+= '%s <br/>' % self.help.help_definition()
                continue
            if line.find("help.cmds")<>-1:
                out+= '%s <br/>' % self.definition
                continue

            print "process:%s"%line
            if line[0]=="!":
                #CMD
                if cmd<>"":
                    out+= self.processCmd(entity,cmd,args,gargs)
                entity=""
                cmd=""
                args={}
                line=line.strip("!")
                line=line.strip()
                entity,cmd=line.split(".",1)
                entity=entity.lower().strip()
                cmd=cmd.lower().strip()
                if self.entityAlias.has_key(entity):
                    entity=self.entityAlias[entity]
                if entity != 'snippet':
                    if not entity in self.entities:
                        out+= '%s <br/>' % self.error("Could not find entity:'%s', on line %s."%(entity,line),help=True)
                        continue

                    if self.cmdAlias[entity].has_key(cmd):
                        cmd=self.cmdAlias[entity][cmd]

                    if not cmd in self.cmds[entity]:
                        out+= '%s <br/>' % self.error("Could not understand command %s, on line %s."%(cmd,line),help=True)
                        continue

            if line.find("=")<>-1:
                name,data=line.split("=",1)
                name=name.lower()
                print "args:%s:%s '%s'"%(name,data,line)
                args[name]=data.strip().replace("\\n","\n")

        if cmd<>"":
            out+=self.processCmd(entity,cmd,args,gargs)
        
        return out

    def processCmd(self,entity,cmd,args,gargs):
        for key,val in gargs.iteritems():
            if not args.has_key(key):
                args[key]=val
        if entity == "snippet":
            if cmd in ('new', 'create', 'c'):
                result = self.snippet.create(**args)
            elif cmd == 'get':
                result = self.snippet.get(**args)
            else:
                result = ''
            return "!%s.%s<br/>%s<br/>" % (entity, cmd, result)
        key="%s__%s"%(entity,cmd)
        result=None
        if self.cmdobj<>None:
            if hasattr(self.cmdobj,key):
                method=eval("self.cmdobj.%s"%key)
                result=method(**args)
        if result==None:
            return self.error("Cannot execute: '%s':'%s' , entity:method not found."%(entity,cmd))
        
        if not j.basetype.string.check(result):
            result=yaml.dump(result, default_flow_style=False).replace("!!python/unicode ","")

        out="!%s.%s<br/>%s<br/>"%(entity,cmd,result)
        return out


        # if j.basetype.list.check(result):
        #     out=""
        #     for item in result:
        #         out+="- %s\n"%item
        #     out+="\n\n"
        #     return out


        # from IPython import embed
        # print "DEBUG NOW yuyuyuy"
        # embed()
        
    def addCmdClassObj(self,cmdo):
        cmdo.txtrobot=self
        self.cmdobj=cmdo

# class YoutrackConnection(object):

#     def __init__(self, url, login,password):
#         """
#         @param url example http://incubaid.myjetbrains.com/youtrack/
#         """
#         yt = 
#         from IPython import embed
#         print "DEBUG NOW opopopo"
#         embed()
        
#         # print yt.createIssue('SB', 'resttest', 'test', 'test', '1', 'Bug', 'Unknown', 'Open', '', '', '')

