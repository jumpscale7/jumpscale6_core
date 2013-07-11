
def main(q,args,params,tags,tasklet):
    params.merge(args)
    
    params.result=""


    doc=params.doc

    if doc.content.find("@DESTRUCTED@")<>-1:
        #page no longer show, destruction message
        doc.destructed=True
        doc.content=doc.content.replace("@DESTRUCTED@","")

    else:
        if doc.destructed==False:
            newdoc="@DESTRUCTED@\n%s"%q.system.fs.fileGetContents(params.doc.path)
            doc.todestruct=True
            q.system.fs.writeFile(params.doc.path,newdoc)

    params.result=("",params.doc)

    return params


def match(q,args,params,tags,tasklet):
    return True

