import ujson

class ZRPC():
    def __init__(self):
        self.args={}
        self.cmd=""
        self.result={}
        self.state=""

    def dumps(self):
        # return msgpack.dumps(self.__dict__)
        return ujson.dumps(self.__dict__)

    def loads(self,s):
        # self.__dict__.update(msgpack.loads(s))
        self.__dict__.update(ujson.loads(s))

    __str__=dumps
    __repr__=dumps

class ZJob():
    def __init__(self, defname="", \
            defcode="",defmd5="",defpath="",\
            defagentid="", \
            jname="", jcategory="", jerrordescr="",\
            jrecoverydescr="", jmaxtime=0, jsource="",\
            juser="", jwait=False,defargs={},executorrole=""):
        self.defname=defname
        self.defcode=defcode
        self.defmd5=defmd5
        self.defpath=defpath
        self.defargs=defargs
        self.defagentid=defagentid
        self.jname=jname
        self.jcategory=jcategory
        self.jerrordescr=jerrordescr
        self.jrecoverydescr=jrecoverydescr
        self.jmaxtime=jmaxtime
        self.jsource=jsource
        self.juser=juser
        self.jwait=jwait
        self.executorrole=executorrole
        self.guid=""        
        self.jresult={}
        self.agent=""
        self.children=[]
        self.parent=""

    def dumps(self):
        # return msgpack.dumps(self.__dict__)
        return ujson.dumps(self.__dict__)

    def loads(self,s):
        # self.__dict__.update(msgpack.loads(s))
        self.__dict__.update(ujson.loads(s))

    __str__=dumps
    __repr__=dumps
 
