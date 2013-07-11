
def main(q,args,params,tags,tasklet):
    params.merge(args)
        
    doc=params.doc
    tags=params.tags
       
    docs=doc.preprocessor.findDocs(filterTagsLabels=tags)          
    
    if tags.tagExists("prefix"):
        prefix=tags.tagGet("prefix")
    else:
        prefix=""

    for doc2 in docs:        
        doc2.parent=doc.name
        doc.children.append(doc2)
        doc2.preprocess()
        
    params.result="",doc
    
    return params


def match(q,args,params,tags,tasklet):
    return True

