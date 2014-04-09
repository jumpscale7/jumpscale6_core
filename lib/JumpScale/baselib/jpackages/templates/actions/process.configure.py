def main(j,jp):
   
    #configure the application to autostart
    
    # jp.log("set autostart $(jp.name)")

    # j.tools.startupmanager.addProcess(\
    #     name=jp.name,\
    #     cmd="", \
    #     args="",\
    #     env={},\
    #     numprocesses=1,\ #if more than 1 process, will be started in tmux as $name_$nr
    #     priority=100,\
    #     shell=False,\
    #     workingdir='',\
    #     jpackage=jp,\
    #     domain=jp.domain,\ 
    #     ports=jp.ports,\ #tcpports
    #     autostart=True,\ #does this app start auto
    #     reload_signal=0,\
    #     user="root",\
    #     log=True,\
    #     stopcmd=None,\ #if special cmd to stop
    #     active=False,\ #enable or disable
    #     check=True,\ #check app to see if it comes active
    #     timeoutcheck=10,\ #how long do we wait to see if app active
    #     isJSapp=1,\  #to tell system if process will self register to redis (is jumpscale app)
    #     upstart=False,\
    #     processfilterstr="")#what to look for when doing ps ax to find the process
    
