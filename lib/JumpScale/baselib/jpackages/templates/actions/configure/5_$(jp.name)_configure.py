def main(j,args,params,tags,tasklet):
   
    #configure the package 

    # #example start with circus
    # args.jp.log("set autostart")
    # cmd = 'python'
    # args2 = 'osisServerStart.py'
    # workingdir = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', 'osis')
    # kwargs = {'stdout_stream.class': 'FileStream', 'stdout_stream.filename': j.system.fs.joinPaths(j.dirs.logDir, 'osis.log'),
    #           'stdout_stream.time_format': '%Y-%m-%d %H:%M:%S', 'stdout_stream.max_bytes': 104857600,
    #           'stdout_stream.backup_count': 3}
    # j.tools.startupmanager.addProcess('osis', cmd, args2, priority=2, workingdir=workingdir, before_start='JumpScale.baselib.circus.CircusManager.checkPort', **kwargs)

    # env_vars = {'WAIT_FOR_PORT': 9200}
    # j.tools.startupmanager.addEnv('osis', env_vars)
    # j.tools.startupmanager.apply()
    
    # args.jp.start()

    return params
    
    
def match(j,args,params,tags,tasklet):
    return True