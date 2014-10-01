import JumpScale.grid.gridhealthchecker
import JumpScale.baselib.redis
import ujson

def main(j, args, params, tags, tasklet):
    doc = args.doc

    dbdata = j.core.grid.healthchecker.checkDBs() 
    out = list()

    results = dbdata[0]
    errors = dbdata[1]

    if errors:
        errors = errors.values()
        for error in errors:
            for dbtype, status in error.iteritems():
                out.append('{color:red}*%s is not alive.*{color}' % dbtype.capitalize())

    if results:
        results = results.values()
        for db in results:
            for dbtype, status in db.iteritems():
                out.append('{color:green}*%s is alive.*{color}' % dbtype.capitalize())
    
    out = '\n'.join(out)
    params.result = (out, doc)
    return params

def match(j, args, params, tags, tasklet):
    return True
