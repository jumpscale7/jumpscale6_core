def main(q,args, params, tags, tasklet):
    print 'hello world'
    import time
    params.merge(args)
    doc=params.doc
    tags=params.tags.getDict()
    spacename = params.paramsExtra['space']
    out=""
    logdir = q.core.appserver6.runningAppserver.webserver.logdir
    backupdir = q.system.fs.joinPaths(logdir, 'backup')
    if 'filename' in tags.keys():
        filen = tags['filename']
        if not q.system.fs.exists(backupdir):
            q.system.fs.createDir(backupdir)
        originalfile = q.system.fs.joinPaths(logdir, filen)
        destfile = q.system.fs.joinPaths(backupdir, "%s_%s" % (time.ctime(), filen))
        q.system.fs.copyFile(originalfile,destfile)
        q.system.fs.writeFile(originalfile, "")

    spaces = q.core.appserver6.runningAppserver.webserver.getSpaces()
    if spacename in spaces:
        sp = q.core.appserver6.runningAppserver.webserver.getSpace(spacename)
    else:
        params.result = (out, params.doc)
        return params
    if spacename == 'system':
        logfiles = q.system.fs.listFilesInDir(logdir)
    else:
        logfiles =  q.system.fs.joinPaths(logdir, 'space_%s.log') % spacename
    for lfile in logfiles:
        baselfile = q.system.fs.getBaseName(lfile)
        out +="|%s | [Reset | /system/ResetAccessLog?filename=%s] | [Show | system/ShowSpaceAccessLog?filename=%s]|\n" % (baselfile,baselfile, baselfile)

    params.result = (out, params.doc)
    return params

def match(q, args, params,  tags, tasklet):
    return True
