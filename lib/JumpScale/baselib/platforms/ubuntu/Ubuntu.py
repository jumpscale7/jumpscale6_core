from JumpScale import j

class Ubuntu:
    def __init__(self):
        self._aptupdated = False
        self._checked = False
        self._cache=None
        self.installedPackageNames=[]

    def initApt(self):
        try:
            import apt
        except ImportError:
            #we dont wont jshell to break, self.check will take of this
            return
        apt.apt_pkg.init()
        if hasattr(apt.apt_pkg, 'Config'):
            cfg = apt.apt_pkg.Config
        else:
            cfg = apt.apt_pkg.Configuration
        try:
            cfg.set("APT::Install-Recommends", "0")
            cfg.set("APT::Install-Suggests", "0")
        except:
            pass
        self._cache = apt.Cache()
        self.aptCache=self._cache
        self.apt=apt

    def check(self, die=True):
        """
        check if ubuntu or mint (which is based on ubuntu)
        """
        if not self._checked:
            try:
                import lsb_release
                info = lsb_release.get_distro_information()['ID']
                if info != 'Ubuntu' and info !='LinuxMint':
                    raise RuntimeError("Only ubuntu or mint supported.")
                self._checked = True
            except ImportError:
                self._checked = False
                if die:
                    raise RuntimeError("Only ubuntu or mint supported.")
        return self._checked

    def getVersion(self):
        """
        returns codename,descr,id,release
        known ids" raring, linuxmint
        """
        self.check()
        import lsb_release
        result=lsb_release.get_distro_information()        
        return result["CODENAME"].lower().strip(),result["DESCRIPTION"],result["ID"].lower().strip(),result["RELEASE"],

    def createUser(self,name,passwd,home=None,creategroup=True):
        import JumpScale.lib.remote.cuisine
        c=j.remote.cuisine.api

        if home==None:
            homeexists=True
        else:
            homeexists=j.system.fs.exists(home)

        c.user_ensure(name, passwd=passwd, home=home, uid=None, gid=None, shell=None, fullname=None, encrypted_passwd=False)
        if creategroup:
            self.createGroup(name)
            self.addUser2Group(name,name)

        if home<>None and not homeexists:
            c.dir_ensure(home,owner=name,group=name)

    def createGroup(self,name):
        import JumpScale.lib.remote.cuisine
        c=j.remote.cuisine.api
        c.group_ensure(name)

    def addUser2Group(self,group,user):
        import JumpScale.lib.remote.cuisine
        c=j.remote.cuisine.api
        c.group_user_ensure(group, user)

            

    def checkInstall(self, packagenames, cmdname):
        """
        @param packagenames is name or array of names of ubuntu package to install e.g. curl
        @param cmdname is cmd to check e.g. curl
        """
        self.check()
        if j.basetype.list.check(packagenames):
            for packagename in packagenames:
                self.checkInstall(packagename,cmdname)
        else:
            packagename=packagenames
            result, out = j.system.process.execute("which %s" % cmdname, False)
            if result != 0:
                self.install(packagename)
            else:
                return
            result, out = j.system.process.execute("which %s" % cmdname, False)
            if result != 0:
                raise RuntimeError("Could not install package %s and check for command %s." % (packagename, cmdname))

    def install(self, packagename):
        self.check()
        if self._cache==None:
            self.initApt()

        if isinstance(packagename, basestring):
            packagename = [packagename]
        for package in packagename:
            pkg = self._cache[package]
            if not pkg.is_installed:
                print "install %s" % packagename
                pkg.mark_install()
        self._cache.commit()
        self._cache.clear()

    def installVersion(self, packageName, version):
        '''
        Installs a specific version of an ubuntu package.

        @param packageName: name of the package
        @type packageName: str

        @param version: version of the package
        @type version: str
        '''

        self.check()
        if self._cache==None:
            self.initApt()

        mainPackage = self._cache[packageName]
        versionPackage = mainPackage.versions[version].package

        if not versionPackage.is_installed:
            versionPackage.mark_install()

        self._cache.commit()
        self._cache.clear()

    def installDebFile(self, path):
        self.check()
        if self._cache==None:
            self.initApt()
        import apt.debfile
        deb = apt.debfile.DebPackage(path, cache=self._cache)
        deb.install()

    def remove(self, packagename):
        j.logger.log("ubuntu remove package:%s"%packagename,category="ubuntu.remove")
        self.check()
        if self._cache==None:
            self.initApt()        
        pkg = self._cache[packagename]
        if pkg.is_installed:
            pkg.mark_delete()
        if packagename in self.installedPackageNames:
            self.installedPackageNames.pop(self.installedPackageNames.index(packagename))
        self._cache.commit()
        self._cache.clear()

    def serviceInstall(self,servicename, daemonpath, args=''):
        C="""
start on runlevel [2345]
stop on runlevel [016]

respawn
"""
        C+="exec %s %s\n"%(daemonpath,args)

        j.system.fs.writeFile("/etc/init/%s.conf"%servicename,C)

    def serviceUninstall(self,servicename):
        self.stopService(servicename)
        j.system.fs.remove("/etc/init/%s.conf"%servicename)

    def startService(self, servicename):
        j.logger.log("start service on ubuntu for:%s"%servicename,category="ubuntu.start")  #@todo P1 add log statements for all other methods of this class
        # self._service(servicename, 'start')
        return j.system.process.execute("start %s" % servicename)

    def stopService(self, servicename):
        # self._service(servicename, 'stop')
        return j.system.process.execute("stop %s" % servicename,False)

    # def _service(self, servicename, action):
    #     return j.system.process.execute("service %s %s" % (servicename, action))


#     def serviceDisableStartAtBoot(self, servicename):
#         self.check()
#         j.system.process.execute("update-rc.d -f %s remove" % servicename)

#     def serviceEnableStartAtBoot(self, servicename):
#         self.check()
#         j.system.process.execute("update-rc.d -f %s defaults" % servicename)

#     def serviceInstall(self, servicename, daemonpath, args=''):
#         """
#         @param daemonpath : path to deamon to start e.g. /usr/local/bin/supervisord
#         """
#         self.check()
#         initdscript="""
# #! /bin/sh
# # Author: Dan MacKinlay <danielm@phm.gov.au>
# # Based on instructions by Bertrand Mathieu
# # http://zebert.blogspot.com/2009/05/installing-django-solr-varnish-and.html

# # Do NOT "set -e"

# # PATH should only include /usr/* if it runs after the mountnfs.sh script
# PATH=/sbin:/usr/sbin:/bin:/usr/bin
# DESC="Description of the service"
# NAME="${name}"
# DAEMON="${daemonpath}"
# DAEMON_ARGS="${daemonargs}"
# PIDFILE=/var/run/$NAME.pid
# SCRIPTNAME=/etc/init.d/$NAME

# # Exit if the package is not installed
# [ -x "$DAEMON" ] || exit 0

# # Read configuration variable file if it is present
# [ -r /etc/default/$NAME ] && . /etc/default/$NAME

# # Load the VERBOSE setting and other rcS variables
# . /lib/init/vars.sh

# # Define LSB log_* functions.
# # Depend on lsb-base (>= 3.0-6) to ensure that this file is present.
# . /lib/lsb/init-functions

# #
# # Function that starts the daemon/service
# #
# do_start()
# {
#     # Return
#     #   0 if daemon has been started
#     #   1 if daemon was already running
#     #   2 if daemon could not be started
#     start-stop-daemon --start --quiet --pidfile $PIDFILE --exec $DAEMON --test > /dev/null \
#         || return 1
#     start-stop-daemon --start --quiet --pidfile $PIDFILE --exec $DAEMON -- \
#         $DAEMON_ARGS \
#         || return 2
#     # Add code here, if necessary, that waits for the process to be ready
#     # to handle requests from services started subsequently which depend
#     # on this one.  As a last resort, sleep for some time.
# }

# #
# # Function that stops the daemon/service
# #
# do_stop()
# {
#     # Return
#     #   0 if daemon has been stopped
#     #   1 if daemon was already stopped
#     #   2 if daemon could not be stopped
#     #   other if a failure occurred
#     start-stop-daemon --stop --quiet --retry=TERM/30/KILL/5 --pidfile $PIDFILE --name $NAME
#     RETVAL="$?"
#     [ "$RETVAL" = 2 ] && return 2
#     # Wait for children to finish too if this is a daemon that forks
#     # and if the daemon is only ever run from this initscript.
#     # If the above conditions are not satisfied then add some other code
#     # that waits for the process to drop all resources that could be
#     # needed by services started subsequently.  A last resort is to
#     # sleep for some time.
#     start-stop-daemon --stop --quiet --oknodo --retry=0/30/KILL/5 --exec $DAEMON
#     [ "$?" = 2 ] && return 2
#     # Many daemons don't delete their pidfiles when they exit.
#     rm -f $PIDFILE
#     return "$RETVAL"
# }

# #
# # Function that sends a SIGHUP to the daemon/service
# #
# do_reload() {
#     #
#     # If the daemon can reload its configuration without
#     # restarting (for example, when it is sent a SIGHUP),
#     # then implement that here.
#     #
#     start-stop-daemon --stop --signal 1 --quiet --pidfile $PIDFILE --name $NAME
#     return 0
# }

# case "$1" in
#   start)
#     [ "$VERBOSE" != no ] && log_daemon_msg "Starting $DESC" "$NAME"
#     do_start
#     case "$?" in
#         0|1) [ "$VERBOSE" != no ] && log_end_msg 0 ;;
#         2) [ "$VERBOSE" != no ] && log_end_msg 1 ;;
#     esac
#     ;;
#   stop)
#     [ "$VERBOSE" != no ] && log_daemon_msg "Stopping $DESC" "$NAME"
#     do_stop
#     case "$?" in
#         0|1) [ "$VERBOSE" != no ] && log_end_msg 0 ;;
#         2) [ "$VERBOSE" != no ] && log_end_msg 1 ;;
#     esac
#     ;;
#   #reload|force-reload)
#     #
#     # If do_reload() is not implemented then leave this commented out
#     # and leave 'force-reload' as an alias for 'restart'.
#     #
#     #log_daemon_msg "Reloading $DESC" "$NAME"
#     #do_reload
#     #log_end_msg $?
#     #;;
#   restart|force-reload)
#     #
#     # If the "reload" option is implemented then remove the
#     # 'force-reload' alias
#     #
#     log_daemon_msg "Restarting $DESC" "$NAME"
#     do_stop
#     case "$?" in
#       0|1)
#         do_start
#         case "$?" in
#             0) log_end_msg 0 ;;
#             1) log_end_msg 1 ;; # Old process is still running
#             *) log_end_msg 1 ;; # Failed to start
#         esac
#         ;;
#       *)
#         # Failed to stop
#         log_end_msg 1
#         ;;
#     esac
#     ;;
#   *)
#     #echo "Usage: $SCRIPTNAME {start|stop|restart|reload|force-reload}" >&2
#     echo "Usage: $SCRIPTNAME {start|stop|restart|force-reload}" >&2
#     exit 1
#     ;;
# esac

# exit 0

# """
#         initdscript=initdscript.replace("${name}",servicename)
#         initdscript=initdscript.replace("${daemonpath}",daemonpath)
#         initdscript=initdscript.replace("${daemonargs}", args)

#         j.system.fs.writeFile("/etc/init.d/%s" % servicename, initdscript)
#         j.system.process.execute("chmod +x /etc/init.d/%s" % servicename)

#         self.serviceEnableStartAtBoot(servicename)



    def updatePackageMetadata(self, force=True):
        self.check()
        if self._cache==None:
            self.initApt()        
        self._cache.update()

    def upgradePackages(self, force=True):
        self.check()
        if self._cache==None:
            self.initApt()        
        self.updatePackageMetadata()
        self._cache.upgrade()

    def getPackageNamesRepo(self):        
        return self._cache.keys()

    def getPackageNamesInstalled(self):
        if self.installedPackageNames==[]:            
            result=[]
            for key in self.getPackageNamesRepo():
                p=self._cache[key]
                if p.installed:
                    self.installedPackageNames.append(p.name)
        return self.installedPackageNames

    def getPackage(self,name):
        return self._cache[name]

    def findPackagesRepo(self,packagename):
        packagename=packagename.lower().strip().replace("_","").replace("_","")
        if self._cache==None:
            self.initApt()        
        result=[]
        for item in self.getPackageNamesRepo():
            item2=item.replace("_","").replace("_","").lower()
            if item2.find(packagename)<>-1:
                result.append(item)
        return result

    def findPackagesInstalled(self,packagename):
        packagename=packagename.lower().strip().replace("_","").replace("_","")
        if self._cache==None:
            self.initApt()        
        result=[]
        for item in self.getPackageNamesInstalled():
            item2=item.replace("_","").replace("_","").lower()
            if item2.find(packagename)<>-1:
                result.append(item)
        return result


    def find1packageInstalled(self,packagename):
        j.logger.log("find 1 package in ubuntu",6,category="ubuntu.find")
        res=self.findPackagesInstalled(packagename)
        if len(res)==1:
            return res[0]
        elif len(res)>1:
            raise RuntimeError("Found more than 1 package for %s"%packagename)
        raise RuntimeError("Could not find package %s"%packagename)

    def listSources(self):
        from aptsources import sourceslist
        return sourceslist.SourcesList()

    def changeSourceUri(self, newuri):
        src = self.listSources()
        for entry in src.list:
            entry.uri = newuri
        src.save()
