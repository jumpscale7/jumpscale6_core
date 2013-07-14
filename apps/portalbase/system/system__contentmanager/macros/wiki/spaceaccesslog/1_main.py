def main(o,args, params,  tags, tasklet, *others):
    params.merge(args)
    doc=params.doc
    tags=params.tags.getDict()
    space = params.paramsExtra['space']
    out=""
    nroflines = int(tags.get('nroflines', 0))
    logdir = o.core.portal.runningPortal.webserver.logdir
    if 'filename' in tags.keys():
        filename = tags['filename']
        logs = q.system.fs.joinPaths(logdir, filename)
    else:
        spaces = o.core.portal.runningPortal.webserver.getSpaces()
        if space in spaces:
            logs = q.system.fs.joinPaths(logdir, 'space_%s.log') % space
        else:
            params.result = (out, params.doc)
            return params
    logcontent = o.system.fs.fileGetContents(logs)
    loglines = logcontent.splitlines()
    out+="||Time || Client ipaddress || User || Page || Full Path||\n"
    for line in loglines[-nroflines:]:
        linecontent = line.split('|')
        out+="|| %s | %s | %s | %s | %s |\n" % (linecontent[0], linecontent[1], linecontent[3], linecontent[4], linecontent[5])
    params.result = (out, params.doc)
    return params

def match(q,args, params, tags, tasklet):
    return True
