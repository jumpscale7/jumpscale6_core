
from JumpScale import j


class MacroHelper():

    def __init__(self):
        pass

    def push2doc(self,args,params,objFetchManipulate):
        params.merge(args)
        doc = params.doc
        
        idd = args.getTag("id")
        if not idd:
            params.result = ('Missing node id param "id"',doc)
            return params

        obj=objFetchManipulate(idd)

        if args.tags.labelExists("show"):
            out=""
            keys=obj.keys()
            keys.sort()
            for key in keys:
                value=obj[key]
                r=0
                for item in str(value).split("\n"):
                    if r==0:
                        out+="- %-20s : %s\n"%(key,item)
                    else:
                        out+="- %-20s   %s\n"%(" ",item)
                    r+=1
            params.result=("{{code:\n%s\n}}"%out,doc)
            return params

        #apply the properties of the object as parameters to the active wiki document
        doc.content=doc.applyParams(obj,content=doc.content)

        #IMPORTANT return 2x doc (not (out,doc)) but return (doc,doc) this tells the appserver that the doc was manipulated
        params.result = (doc, doc)
        return params
    
