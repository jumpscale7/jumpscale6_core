
from JumpScale import j
import gevent

import JumpScale.grid.zdaemon

j.application.start("jumpscale:blobserver2_parent")
j.application.initGrid()

import JumpScale.baselib.blobstor2

j.logger.consoleloglevel = 2


j.servers.blobstor2.start(port=2346)


j.application.stop()



# import inspect
# import ujson

# class BlobserverCMDS():

#     def __init__(self, daemon):

#         j.application.initGrid()

#         self.daemon = daemon
#         self.adminpasswd = j.application.config.get('grid.master.superadminpasswd')
#         self.adminuser = "root"

#         self.STORpath="/opt/STOR"  #harccoded for now needs to come from HRD

#         # j.logger.setLogTargetLogForwarder()

#     def _getPaths(self,namespace,key):
#         backuppath=j.system.fs.joinPaths(self.STORpath,namespace,key[0:2],key[2:4],key)
#         mdpath=backuppath+".md"
#         return backuppath,mdpath

#     def set(self,namespace,key,value,repoId="",serialization="",session=None):
#         if serialization=="":
#             serialization="lzma"

#         backuppath,mdpath=self._getPaths(namespace,key)

#         if not(key<>"" and self.exists(namespace,key)):
#             md5=j.tools.hash.md5_string(value)
#             j.system.fs.createDir(j.system.fs.getDirName(backuppath))
#             j.system.fs.writeFile(backuppath,value)


#         if not j.system.fs.exists(path=mdpath):
#             md={}
#             md["md5"]=md5
#             md["format"]=serialization
#         else:
#             md=ujson.loads(j.system.fs.fileGetContents(mdpath))
#         if not md.has_key("repos"):
#             md["repos"]={}
#         md["repos"][str(repoId)]=True
#         mddata=ujson.dumps(md)
#         # print "Set:%s"%md
#         j.system.fs.writeFile(backuppath+".md",mddata)
#         return [key,True,True]

#     def get(self,namespace,key,serialization="",session=None):
#         if serialization=="":
#             serialization="lzma"

#         backuppath,mdpath=self._getPaths(namespace,key)

#         md=ujson.loads(j.system.fs.fileGetContents(mdpath))
#         if md["format"]<>serialization:
#             raise RuntimeError("Serialization specified does not exist.") #in future can convert but not now
#         with open(backuppath) as fp:
#             data2 = fp.read()
#             fp.close()
#         return data2

#     def getMD(self,namespace,key,session=None):
#         if session<>None:
#             self._adminAuth(session.user,session.passwd)

#         backuppath,mdpath=self._getPaths(namespace,key)

#         return ujson.loads(j.system.fs.fileGetContents(mdpath))

#     def delete(self,namespace,key,repoId="",force=False,session=None):
#         if force=='':
#             force=False #@todo is workaround default values dont work as properly, when not filled in always ''
#         if session<>None:
#             self._adminAuth(session.user,session.passwd)

#         if force:
#             backuppath,mdpath=self._getPaths(namespace,key)
#             j.system.fs.remove(backuppath)
#             j.system.fs.remove(mdpath)
#             return

#         if key<>"" and not self.exists(namespace,key):
#             return

#         backuppath,mdpath=self._getPaths(namespace,key)

#         if not j.system.fs.exists(path=mdpath):
#             raise RuntimeError("did not find metadata")
#         md=ujson.loads(j.system.fs.fileGetContents(mdpath))
#         if not md.has_key("repos"):
#             raise RuntimeError("error in metadata on path:%s, needs to have repos as key."%mdpath)
#         if md["repos"].has_key(str(repoId)):
#             md["repos"].pop(str(repoId))
#         if md["repos"]=={}:
#             j.system.fs.remove(backuppath)
#             j.system.fs.remove(mdpath)
#         else:
#             mddata=ujson.dumps(md)
#             j.system.fs.writeFile(backuppath+".md",mddata)

#     def exists(self,namespace,key,repoId="",session=None):
#         backuppath,mdpath=self._getPaths(namespace,key)
#         if repoId=="":
#             return j.system.fs.exists(path=backuppath)
#         if j.system.fs.exists(path=backuppath):
#             md=ujson.loads(j.system.fs.fileGetContents(mdpath))
#             return md["repos"].has_key(str(repoId))
#         return False

#     def deleteNamespace(self,namespace,session=None):
#         if session<>None:
#             self._adminAuth(session.user,session.passwd)
#         backuppath=j.system.fs.joinPaths(self.STORpath,namespace)
#         j.system.fs.removeDirTree(backuppath)


#     def _adminAuth(self,user,passwd):
#         if user != self.adminuser or passwd != self.adminpasswd:
#             raise RuntimeError("permission denied")


# daemon = j.servers.zdaemon.getZDaemon(port=2345)

# daemon.setCMDsInterface(BlobserverCMDS, category="blobserver")  # pass as class not as object !!! chose category if only 1 then can leave ""

# cmds=daemon.daemon.cmdsInterfaces["blobserver"][0]
# # cmds.loadJumpscripts()

# daemon.start()


