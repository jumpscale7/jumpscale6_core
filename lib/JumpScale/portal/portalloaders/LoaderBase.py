from JumpScale import j


class LoaderBaseObject():

    def __init__(self, type):
        self.model = None
        self.type = type
        # self._osis=None

    def _createDefaults(self, path, items):
        base = j.system.fs.joinPaths(j.core.portalloader.getTemplatesPath(), ".%s" % self.type)
        items += ["main.cfg", "acl.cfg"]
        for item in items:
            dest = j.system.fs.joinPaths(path, ".%s" % self.type, item)
            if not j.system.fs.exists(dest):
                source = j.system.fs.joinPaths(base, item)
                j.system.fs.copyFile(source, dest)

    def _loadFromDisk(self, path, reset=False):
        # path=path.replace("\\","/")
        print "loadfromdisk:%s" % path

        # remove old cfg and write new one with only id
        cfgpath = j.system.fs.joinPaths(path, ".%s" % self.type, "main.cfg")

        if not j.system.fs.exists(cfgpath):
            self.createDefaults(path)

        # if j.system.fs.exists(cfgpath):
            # ini=j.tools.inifile.open(cfgpath)
        # if ini.checkParam("main","name"):
        j.system.fs.remove(cfgpath)
        ini = j.tools.inifile.new(cfgpath)
        ini.addSection("main")
        ini.setParam("main", "id", j.system.fs.getDirName(path, True))
        ini.write()

        osis = j.apps.system.contentmanager.models.__dict__["%s" % self.type]

        obj = osis.ini2object(cfgpath, limitVars=["id"])

        obj.path = path
        # self._osis.set(obj)
        self.model = obj
        self.processAcl()

    def processUsers(self, cfgdir=None):
        if cfgdir == "":
            cfgfile = j.system.fs.joinPaths(self.model.path, ".%s" % self.type, "users.cfg")
        else:
            cfgfile = j.system.fs.joinPaths(cfgdir, "users.cfg")

        def iniManipulator(ini, section, existsInDb, obj, objFromIni, args):
            # for each obj this will be called
            # can manipulate the inifile or obj
            objFromIni.groups = [item.lower() for item in objFromIni.groups]
            skip = False

            if existsInDb:
                reset = False
                if ini.checkParam(section, "reset"):
                    if str(ini.getValue(section, "reset")) == "1":
                        reset = True
                if not reset:
                    # means is in actors,space or bucket cannot overwrite existing object when from system
                    print "skipped user insert for user %s because already created by system." % objFromIni.id
                    return ini, obj, objFromIni, True  # will not use this entry from the config file

            if objFromIni.id.find("@") != -1 and objFromIni.emails == "":
                # email in id needs to be set as email in obj
                objFromIni.emails = [obj.id]
                ini.setParam(section, "emails", objFromIni.id)
            if ini.checkParam(section, "key"):
                objFromIni.secret = ini.getValue(section, "key")
                ini.setParam(section, "secret", objFromIni.secret)  # for backwards compatibility, no longer required
            if objFromIni.secret == "":
                objFromIni.secret = objFromIni.guid.replace("-", "")[:9]
                if not ini.checkParam(section, "secret") or (ini.checkParam(section, "secret") and ini.getValue(section, "secret").lower() != "none"):
                    ini.setParam(section, "secret", objFromIni.secret)
            if objFromIni.passwd == "":
                objFromIni.passwd = objFromIni.secret
                # ini.setParam(section,"passwd",obj.passwd)
            return ini, obj, objFromIni, skip

        args = {}
        objs = j.apps.system.usermanager.models.user.ini2objects(
            cfgfile, overwriteInDB=False, ignoreWhenNotExist=True, manipulator=iniManipulator, manipulatorargs=args, writeIni=False)
        for obj in objs:
            print "ACL User Found:%s with secret:%s and groups:%s" % (obj.id, obj.secret, ",".join(obj.groups))
            j.core.portal.runningPortal.webserver.userKeyToName[obj.secret] = obj.id

        # populate groups
        for obj in objs:
            for groupname in obj.groups:
                if not j.apps.system.usermanager.models.group.exists(id=groupname):
                    group = j.apps.system.usermanager.models.group.new()
                    group.id = groupname
                    j.apps.system.usermanager.models.group.set(group)
                else:
                    group = j.apps.system.usermanager.models.group.get(id=groupname)
                if not obj.id in group.members:
                    group.members.append(obj.id)
                    j.apps.system.usermanager.models.group.set(group)

    def processAcl(self, cfgdir=""):
        # populate acl
        if cfgdir == "":
            cfgfile = j.system.fs.joinPaths(self.model.path, ".%s" % self.type, "acl.cfg")
        else:
            cfgfile = j.system.fs.joinPaths(cfgdir, "acl.cfg")

        lines = j.system.fs.fileGetContents(cfgfile).split("\n")
        for line in lines:
            line = line.strip()
            if line.strip() == "" or line[0] == "#":
                continue
            for separator in ["=", ":"]:
                if line.find(separator) != -1:
                    name, rights = line.split(separator)
                    name = name.lower().strip()
                    rights = str(rights.lower().strip())
                    self.model.acl[name] = rights
                    # print "ACE:%s %s"%(name,rights)
        self.save()

    def save(self):
        if self.type and self.model:
            j.apps.system.contentmanager.models.__dict__["%s" % self.type].set(self.model)

    def deleteOnDisk(self):
        j.system.fs.removeDirTree(self.model.path)

    def reset(self):
        self.loadFromDisk(self.model.path, reset=True)


class LoaderBase():

    def __init__(self, type, objectClass):
        """
        """
        self.id2object = {}
        self.__dict__["%ss" % type] = self.id2object
        self.type = type
        self._objectClass = objectClass

    def getLoaderFromId(self, id):
        id = id.lower()
        if id in self.id2object:
            return self.id2object[id]
        else:
            raise RuntimeError("Could not find loader with id %s" % id)

    def removeLoader(self, id):
        id = id.lower()
        if id in self.id2object:
            self.id2object.pop(id)
            loader = self.__dict__["%ss" % self.type]
            if id in loader:
                loader.pop(id)

    def _getSystemLoaderForUsersGroups(self):
        lba = LoaderBaseObject("")
        userspath = j.system.fs.joinPaths(j.core.portal.runningPortal.cfgdir, 'users')
        if not j.system.fs.exists(userspath):
            ini = j.config.getInifile(userspath)
            ini.addSection('admin')
            ini.addParam('admin', 'passwd', 'admin')
            ini.addParam('admin', 'groups', 'admin')
            ini.addParam('admin', 'reset', '1')
            ini.addSection('guest')
            ini.addParam('guest', 'passwd', '')
            ini.addParam('guest', 'groups', 'guest')
            ini.addParam('guest', 'reset', '1')

        lba.processUsers(j.core.portal.runningPortal.cfgdir)

    def scan(self, path, reset=False):

        items = [j.system.fs.pathNormalize(item.replace(".%s" % self.type, "") + "/") for
                 item in j.system.fs.listDirsInDir(path, True, False, True)
                 if j.system.fs.getDirName(item + "/", True) == ".%s" % self.type]

        for path in items:
            object = self._objectClass()
            result = object.loadFromDisk(path, reset)
            if result != False:
                # print "load object %s" % path
                self.id2object[object.model.id.lower()] = object
