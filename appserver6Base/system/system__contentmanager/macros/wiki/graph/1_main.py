
def main(q,args,params,tags,tasklet):
    params.merge(args)
    
    doc=params.doc
    tags=params.tags

    out=""
    cmdstr=params.macrostr.split(":",1)[1].replace("}}","").strip()
    md5=q.tools.hash.md5_string(cmdstr)
    q.system.fs.createDir(q.system.fs.joinPaths(q.core.appserver6.runningAppserver.webserver.filesroot,"dot"))
    path=q.system.fs.joinPaths(q.core.appserver6.runningAppserver.webserver.filesroot,"dot",md5)
    if not q.system.fs.exists(path+".png"):
        q.system.fs.writeFile(path+".dot",cmdstr)
        cmd="dot -Tpng %s.dot -o %s.png" %(path,path)
        
        # for i in range(5):
        rescode,result=q.system.process.execute(cmd)
            # if result.find("warning")==011:

        if result.find("warning")<>-1:
            out=result
            out+='\n'
            out+="##DOT FILE WAS##:\n"
            out+=cmdstr
            out+="##END OF DOT FILE##\n"
            out="{{code:\n%s\n}}"%out

            params.result=out

            return params

    
    out="!/root/dot/%s.png!"%md5        

    params.result=(out,doc)

    return params


def match(q,args,params,tags,tasklet):
    return True

