from JumpScale import j

descr = """
check timeout jobs
"""

organization = "jumpscale"
author = "khamisr@codescalers.com"
license = "bsd"
version = "1.0"
category = "system.backup.osis"
period = 60*60*24
enable = True
async = True
roles = ["admin"]
queue ='io'

def action():
    import JumpScale.grid.osis
    import tarfile
    """
    Backs up each category under {var directory}/osisbackup/namespace/category/
    Creates a targz of the backup under {var directory}/osisbackup_{timestamp}
    """
    backuppath = j.system.fs.joinPaths(j.dirs.varDir, 'osisbackup')
    timestamp = j.base.time.getTimeEpoch() 
    try:
        oscl = j.core.osis.getClient(user='root')
        namespaces = oscl.listNamespaces()
        if j.system.fs.exists(backuppath):
            j.system.fs.removeDirTree(backuppath)
        for namespace in namespaces:
            categories = oscl.listNamespaceCategories(namespace)
            for category in categories:
                if namespace == 'system' and category in ['stats', 'log']:
                    continue
                outputpath = j.system.fs.joinPaths(backuppath, namespace, category)
                j.system.fs.createDir(outputpath)
                oscl.export(namespace, category, outputpath)

        #targz
        outputpath = j.system.fs.joinPaths(j.dirs.varDir, 'osisbackup_%s.tar.gz' % timestamp)
        with tarfile.open(outputpath, "w:gz") as tar:
            tar.add(backuppath)
    except Exception:
        import JumpScale.baselib.mailclient
        import traceback
        error = traceback.format_exc()
        message = '''
OSIS backup at %s failed.
Data should have been backed up to %s on the admin node.

Exception:
-----------------------------
%s
-----------------------------
    ''' % (j.base.time.epoch2HRDateTime(timestamp), backuppath, error)
        message = message.replace('\n', '<br/>')
        j.clients.email.send('support@mothership1.com', 'smtp@incubaid.com', 'OSIS backup failed', message)
        

