def main(o, args, params,  tags, tasklet):        
    doc=args.doc
    tags=args.tags
       
    docs=doc.preprocessor.findDocs(filterTagsLabels=tags)
    # To avoid the document including itself (causing infinite recursion), remove itself from the list of selected docs
    docs = [d for d in docs if d.name.lower() != doc.name.lower()]
    if tags.tagExists("heading"):
        headinglevel=tags.tagGet("heading")
    else:
        headinglevel=2        
    
    out=""
    for d in docs:
        d.content=d.source #make sure we restart from original source when doing the includes (only for include we do this)
        d.preprocess()
        out+="h%s. %s\n\n" % (headinglevel, d.title)
        out+="%s\n" % d.content
        
    params.result=(out, doc)
    
    return params


def match(o, args, params,  tags, tasklet):
    return True
