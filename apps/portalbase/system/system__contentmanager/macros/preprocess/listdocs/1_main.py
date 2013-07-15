def main(o,args,params,tags,tasklet):
    params.merge(args)
        
    doc2=params.doc
    tags=params.tags
       
    docs=doc2.preprocessor.findDocs(filterTagsLabels=tags)       

    out=""
    for doc in docs:
        doc.preprocess()
        out+="* [%s]\n" % doc.pagename
    params.result=(out,doc2)
    
    return params


def match(o,args,params,tags,tasklet):
    return True
