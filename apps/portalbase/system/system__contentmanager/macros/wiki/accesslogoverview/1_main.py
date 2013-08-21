def main(o,args, params, tags, tasklet):
    print 'hello world'
    import time
    params.merge(args)
    doc=params.doc
    tags=params.tags.getDict()
    spacename = params.paramsExtra['space']
    out=""
    logdir = o.core.portal.runningPortal.webserver.logdir
    backupdir = o.system.fs.joinPaths(logdir, 'backup')
    if 'filename' in tags.keys():
        filen = tags['filename']
        if not o.system.fs.exists(backupdir):
            o.system.fs.createDir(backupdir)
        originalfile = o.system.fs.joinPaths(logdir, filen)
        destfile = o.system.fs.joinPaths(backupdir, "%s_%s" % (time.ctime(), filen))
        o.system.fs.copyFile(originalfile,destfile)
        o.system.fs.writeFile(originalfile, "")

    spaces = o.core.portal.runningPortal.webserver.getSpaces()
    if spacename in spaces:
        sp = o.core.portal.runningPortal.webserver.getSpace(spacename)
    else:
        params.result = (out, params.doc)
        return params
    if spacename == 'system':
        logfiles = o.system.fs.listFilesInDir(logdir)
    else:
        logfiles =  o.system.fs.joinPaths(logdir, 'space_%s.log') % spacename
    for lfile in logfiles:
        baselfile = o.system.fs.getBaseName(lfile)
        out +="|%s | [Reset | /system/ResetAccessLog?filename=%s] | [Show | system/ShowSpaceAccessLog?filename=%s]|\n" % (baselfile,baselfile, baselfile)

    params.result = (out, params.doc)
    return params

def match(o, args, params,  tags, tasklet):
    return True
