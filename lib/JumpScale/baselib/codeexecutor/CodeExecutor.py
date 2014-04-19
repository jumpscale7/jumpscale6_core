from JumpScale import j

class CodeExecutor:
    def __init__(self):
       pass

    def _getMacroCandidates(self, txt):
        result = []
        items = txt.split("{{")
        for item in items:
            if item.find("}}") != -1:
                item = item.split("}}")[0]
                if item not in result:
                    result.append("{{%s}}" % item)
        return result

    def eval(self,code):
        candidates=self._getMacroCandidates(code)
        for itemfull in candidates:
            item=itemfull.strip("{{").strip("}}")
            try:
                result=eval(item)
            except Exception,e:
                raise RuntimeError("Could not execute code in codeExecutor,%s\n%s,Error was:%s"%(item,code,e))
            result=self._tostr(result)
            code=code.replace(itemfull,result)
        return code

    def evalFile(self,path):
        content=j.system.fs.fileGetContents(path)
        content=self.eval(content)
        j.system.fs.writeFile(path,content)

    def _tostr(self,result):
        if result==None:
            result=""
        elif j.basetype.boolean.check(result):
            if result==True:
                result=1
            else:
                result=0
        elif j.basetype.integer.check(result) or j.basetype.float.check(result) or j.basetype.string.check(result):
            result=str(result)
        elif j.basetype.list.check(result):
            resout=""
            for item in result:
                resout+="%s,"%self._tostr(item)
            result=resout.strip(",")
        elif j.basetype.dictionary.check(result):
            resout=""
            for key in result.keys():
                val=result[key]
                val=self._tostr(val)
                resout+="%s::%s,"%(key,val)
            result=resout.strip(",")
        else:
            raise RuntimeError("Could not convert %s to string"%result)
        return result




        from IPython import embed
        print "DEBUG NOW macroeval"
        embed()
        

