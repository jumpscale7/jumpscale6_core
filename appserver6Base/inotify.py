import platform

from pylabs.InitBase import q,i


q.qshellconfig.interactive=True

import os

try:
    #from pyinotify import WatchManager, Notifier, ThreadedNotifier, EventsCodes, ProcessEvent
    import gevent_inotifyx as inotify
except:
    #q.system.platform.ubuntu.install("python-pyinotify")
    #q.system.platform.ubuntu.install("python-pyinotify-doc")
    q.system.platform.ubuntu.install("python-inotifyx")
    import gevent_inotifyx as inotify

import gevent
import gevent_inotifyx as inotify
from gevent.queue import Queue

client=q.core.appserver6.getAppserverClient("127.0.0.1",9999,"1234")
systemActor=client.getActor("system","contentmanager",instance=0)

class watcher():
    def __init__(self,contentmgr):
        self.fd=None
        self.contentmgr=contentmgr
        self.ddirs={}
        self.paths=[]
        #self.q = Queue()
        
    def watchDirAndSubDir(self,path):
        self.paths.append(path)
    
    def start(self):
        self.fd=inotify.init()
        self.ddirs={}
        for startpath in self.paths:
            for ddir in q.system.fs.listDirsInDir(startpath,True):
                ddirname=q.system.fs.getDirName(ddir+"/",True)
                #print ddirname
                ok=True
                if ddirname.find(".")==0 or ddir.find(".cache")<>-1:
                    ok=False
                    
                if ok:
                    try:
                        wd = inotify.add_watch(self.fd, ddir, inotify.IN_CREATE | inotify.IN_DELETE \
                                           | inotify.IN_DELETE_SELF | inotify.IN_MODIFY \
                                           | inotify.IN_MOVE_SELF | inotify.IN_MOVED_FROM \
                                           | inotify.IN_MOVED_TO) 
                        #print "add notify %s" % ddir
                        self.ddirs[wd]=ddir  
                    except:
                        print "ERROR COULD NOT ADD notify %s" % ddir
                        
                
        print "started"
        while True:
            events = inotify.get_events(self.fd)
            for event in events:
                #q.put(event)
                if event.name<>None:
                    path=self.ddirs[event.wd]+"/"+event.name
                else:
                    path=self.ddirs[event.wd]
                    print "restarted for %s" % path
                    self.start()
                    
                
                if path.find(".goutputstream")<>-1:
                    continue
                
                print "received event:", event.get_mask_description(),path
                
                if q.system.fs.isFile(path):
                    if q.system.fs.getFileExtension(path).lower() in ["wiki","py","spec"]:
                        try:
                            self.contentmgr.notifychange(path)
                            print "notified %s" % path
                        except:
                            print "could not notify change for %s" % path
                elif q.system.fs.isDir(path):
                    print "restarted for dir %s" % path
                    self.start()
                    
            

watcher=watcher(systemActor)
watcher.watchDirAndSubDir("/root/Dropbox")
watcher.start()

q.application.stop()

#gevent.spawn(event_producer, fd, q)

while True:
   event = q.get()
   print "received event:", event.get_mask_description(), event.name

from pylabs.Shell import ipshell
print '[DEBUG] - Now'
ipshell()


