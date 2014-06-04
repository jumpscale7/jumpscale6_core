from JumpScale import j

descr = """
backup vfw config files
"""

organization = "jumpscale"
author = "khamisr@codescalers.com"
license = "bsd"
version = "1.0"
category = "vfw.backup.config"
period = 60*60*24
enable = True
async = True
roles = ["admin"]
queue ='io'

def action():
    import JumpScale.grid.osis
    import tarfile
    import JumpScale.baselib.mailclient

    backuppath = j.system.fs.joinPaths(j.dirs.varDir, 'vfwbackup')
    timestamp = j.base.time.getTimeEpoch() 
    vfwerrors = list()
    try:
        import JumpScale.lib.routeros
        if j.system.fs.exists(backuppath):
            j.system.fs.removeDirTree(backuppath)

        osiscl = j.core.osis.getClient(user='root')
        vfwcl = j.core.osis.getClientForCategory(osiscl, 'vfw', 'virtualfirewall')
        cscl = j.core.osis.getClientForCategory(osiscl, 'cloudbroker', 'cloudspace')

        routeros_password = j.application.config.get('vfw.admin.passwd')

        notdestroyed = {'query': {'bool': {'must_not': [{'term': {'status': 'destroyed'}}]}}}
        cloudspaces = cscl.simpleSearch({}, nativequery=notdestroyed)
        cloudspaceids = [cloudspace['id'] for cloudspace in cloudspaces]

        alivevfws = {'query': {'bool': {'must': [{'terms': {'domain': cloudspaceids}}]}}}
        vfws = vfwcl.simpleSearch({}, nativequery=alivevfws)

        for vfw in vfws:
            try:
                routeros = j.clients.routeros.get(vfw['host'], 'vscalers', routeros_password)
                name = vfw['name'] or vfw['domain']
                path = j.system.fs.joinPaths(backuppath, name)
                routeros.backup(name, path)
            except Exception:
                vfw['pubips'] = ', '.join(vfw['pubips'])
                vfwerrors.append('NAME: %(name)s      DOMAIN: %(domain)s      HOST: %(host)s      PUBLIC IP: %(pubips)s' % vfw) 


        #targz
        outputpath = j.system.fs.joinPaths(j.dirs.varDir, 'vfwbackup_%s.tar.gz' % timestamp)
        with tarfile.open(outputpath, "w:gz") as tar:
            tar.add(backuppath)
    except Exception:
        import traceback
        error = traceback.format_exc()
        message = '''
VFW backup at %s failed.
Data should have been backed up to %s on the admin node.

Exception:
-----------------------------
%s
-----------------------------
    ''' % (j.base.time.epoch2HRDateTime(timestamp), backuppath, error)
        message = message.replace('\n', '<br/>')
        j.clients.email.send('support@mothership1.com', 'monitor@mothership1.com', 'VFW backup failed', message)
    finally:
        if vfwerrors:
            message = '''
    VFW backup at %s failed.
    Data should have been backed up to %s on the admin node.

    These vfws have failed to backup:
    -----------------------------
    %s
    -----------------------------
        ''' % (j.base.time.epoch2HRDateTime(timestamp), backuppath, '<br/>'.join(vfwerrors))
            message = message.replace('\n', '<br/>')
            j.clients.email.send('support@mothership1.com', 'smtp@incubaid.com', 'VFW backup incomplete', message)
        

