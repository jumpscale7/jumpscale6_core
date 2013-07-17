def main(o,args,params,tags,tasklet):
    params.merge(args)
        
    doc=params.doc
    tags=params.tags
       
    docs=doc.preprocessor.findDocs(filterTagsLabels=tags)
    docs = [d for d in docs if d.name.lower() != doc.name.lower() and 'docs' not in d.name.lower()]
        
    out=""
    for child_doc in docs:
        out+="* [%s]\n" % child_doc.pagename
        
    params.result=(out,doc)

    out=""
    for doc in docs:
        doc.preprocess()
        out+="* [%s]\n" % doc.pagename
    params.result=(out,doc2)
    
    return params


def match(o,args,params,tags,tasklet):
    return True
