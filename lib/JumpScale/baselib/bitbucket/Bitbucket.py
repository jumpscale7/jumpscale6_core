import json
from JumpScale import j
from JumpScale.core.baseclasses import BaseEnumeration

from BitbucketConfigManagement import *
import urllib

class BitbucketRESTCall(BaseEnumeration):
    """
    Enumerator of all supported Bitbucket REST calls
    """

    def __init__(self, value=None):
        self.value = value

    @classmethod
    def _initItems(cls):
        cls.registerItem('groups')
        cls.registerItem('group_privileges', value='group-privileges')
        cls.registerItem('users')
        cls.registerItem('repositories')
        cls.registerItem('user')
        cls.finishItemRegistration()

class BitbucketSettingsParam(BaseEnumeration):
    """
    Enumerator of all supported Bitbucket permissions
    """

    @classmethod
    def _initItems(cls):
        cls.registerItem('name')
        cls.registerItem('permission')
        cls.registerItem('auto_add')
        cls.finishItemRegistration()

class BitbucketPermission(BaseEnumeration):
    """
    Enumerator of all supported Bitbucket permissions
    """

    @classmethod
    def _initItems(cls):
        cls.registerItem('read')
        cls.registerItem('write')
        cls.registerItem('admin')
        cls.finishItemRegistration()

class Bitbucket:
    """
    Bitbucket client enables administrators and developers leveraging Bitbucket services through JumpScale

    @property accounts = account on bitbucket e.g. despieg, value is array of mercurial repo's
    """

    def __init__(self):
        self._accountnames= list()
        self._initialized = False
        self.accountsLocalRepoNames = dict()
        self.accountsRemoteRepoNames = dict()
        self.apiVersion = '1.0'
        self.apiURI = 'https://api.bitbucket.org'
        self.resultFormat = "json"
        self.codedir = j.system.fs.joinPaths(j.dirs.baseDir, ".." , "code")
        j.system.fs.createDir(self.codedir)
        self.config=BitbucketConfigManagement()
        self.connections={}
        j.logger.consolelogCategories.append("bitbucket")

    def log(self,msg,category="",level=5):
        category="bitbucket.%s"%category
        category=category.rstrip(".")
        j.logger.log(msg,category=category,level=level)


    def _init(self,force=False):
        pass
        #if force or not self._initialized:
            #self.getAccountNames()
            #for account in self._accountnames:
                #repos=self.getRepoNamesLocal(account)
                #self.accountsLocalRepoNames[account]=repos
        self._initialized=True

    #def getRepoNamesLocal(self,account=None):
        #if account<>None:
            #bitbucket_connection = BitbucketConnection(account)
            #return bitbucket_connection.getRepoNamesLocal()
        
        #for account in self._accountnames:
            #bitbucket_connection = BitbucketConnection(account)
            #return bitbucket_connection.getRepoNamesLocal()

    #def getAccountNames(self):
        #names = j.clients.bitbucket.config.list()
        #self._accountnames = names
        #return names

    #def pull(self,message="",update=True,merge=True):
        #"""
        #pull repo to local location
        #@update if update will update local repo
        #@merge if merge will try an merge local repo
        #"""        
        #for account in self.getAccountNames():
            #conn=self.getBitbucketConnection(account)
            #conn.pull(message=message)
            
    #def push(self,message="",commit=True,addremove=True):
        #"""
        #pull repo to local location
        #@commit before pushing will commit
        #@addremove before pushing will addremove
        #"""           
        #if commit ==False & addremove==True:
            #raise RuntimeError("Do not support to addremove files without committing")
        #if commit or addremove:
            #self.commit(message=message,addremove=addremove)     
        #for account in self.getAccountNames():
            #conn=self.getBitbucketConnection(account)
            #conn.push(message=message,commit=commit,addremove=addremove)            
            
    #def commit(self,message="",addremove=True):
        #"""
        #commit all changes & 
        #"""
        
        #self.pull(message)
        #for account in self.getAccountNames():
            #conn=self.getBitbucketConnection(account)
            #conn.commitPush(message=message)

    def accountAdd(self,account="",login="",passwd=""):
        """
        All params need to be filled in, when 1 not filled in will ask all of them
        """
        if account<>"" and login<>"" and passwd<>"":
            try:
                self.config.remove(account)
            except:
                pass
            self.config.add(account, {"login": login, "passwd": passwd})
        else:
            self.config.add()

    def accountsReview(self,accountName=""):
        self.config.review(accountName)

    def accountsShow(self):
        self.config.show()

    def accountsRemove(self,accountName=""):
        self.config.remove(accountName)

    def _accountGetConfig(self,accountName=""):
        if accountName not in self.config.list():
            j.console.echo("Did not find account name %s for bitbucket, will ask for information for this account" % accountName)
            self.config.add(accountName)

        return self.config.getConfig(accountName)

    def _accountGetLoginInfo(self,accountName=""):
        """
        """
        self._init()
        if accountName=="":
            accountName=j.gui.dialog.askChoice("Select Bitbucket account name",self._getAccountNames())
        config=self._accountGetConfig(accountName)
        login=config["login"]
        if login.find("@login")<>-1:
            if j.application.shellconfig.interactive:
                login=j.gui.dialog.askString("  \nLogin for bitbucket account %s"%accountName)
            else:
                login = ""
            self.config.configure(accountName,{'login': login})
        passwd=config["passwd"]
        if passwd.find("@passwd")<>-1:
            if j.application.shellconfig.interactive:
                passwd=j.gui.dialog.askPassword("  \nPassword for bitbucket account %s"%accountName, confirm=False)
            else:
                passwd = ""
            self.config.configure(accountName,{'passwd': passwd})
        
        if j.application.shellconfig.interactive and (login=="" or passwd==""):
            self.accountsReview(accountName)
        if login and passwd and login not in ('hg', 'ssh'):
            url=" https://%s:%s@bitbucket.org/%s/" % (login,passwd,accountName)
        else:
            url=" ssh://hg@bitbucket.org/%s/" % (accountName)
        return url,login,passwd

    def getBitbucketConnection(self, accountName ):
        self._init()
        url,accountLogin,accountPasswd = self._accountGetLoginInfo(accountName)
        if self.connections.has_key(accountName):
            return self.connections[accountName]
        bitbucket_connection = BitbucketConnection(accountName)
        return bitbucket_connection
        
    def getRepoConnection(self, accountName, reponame,branch="default"):
        self._init()
        bitbucket_connection = BitbucketConnection(accountName)
        return bitbucket_connection.getMercurialClient(reponame,branch=branch)


        '''
        if j.application.shellconfig.interactive:
            if not accountName:
                accountName=j.gui.dialog.askChoice("Select bitbucket accountName",self._getAccountNames())

            accounts = self._getAccountNames()
            if not accountName in accounts:
                if not accountLogin:
                    accountLogin = j.gui.dialog.askString("Please enter account Login:")
                if not accountPasswd or accountPasswd=="@passwd":
                    accountPasswd = j.gui.dialog.askPassword("Please enter account Password", True)                
                self.accountAdd(accountName, accountLogin, accountPasswd)

            if self.config.getConfig(accountName)["passwd"].lower().strip()=="@passwd":
                if not accountLogin:
                    accountLogin = j.gui.dialog.askString("Please enter account Login:")
                if not accountPasswd or accountPasswd=="@passwd":
                    accountPasswd = j.gui.dialog.askPassword("Please enter account Password", True)
                self.accountAdd(accountName, accountLogin, accountPasswd)
        '''       


class BitbucketConnection(object):

    def __init__(self, accountName):
        self.accountName = accountName
        #self.codedir = j.system.fs.joinPaths(j.dirs.baseDir, ".." , "code")
        self.codedir=j.dirs.codeDir
        self.bitbucket_client = j.clients.bitbucket
        self.accountPathLocal = j.system.fs.joinPaths(self.codedir,accountName)
        j.system.fs.createDir(self.accountPathLocal )
        self.bitbucketclients={}
        self.ignoredrepos=[]
        self.activerepos=[]
        self._init()
        
    def _init(self):
        self.lastactionstatusFile=j.system.fs.joinPaths(self.accountPathLocal,".lastactionstatus")         
        if j.system.fs.exists(self.lastactionstatusFile):
            for line in j.system.fs.fileGetContents(self.lastactionstatusFile).split("\n"):
                line.strip().lower()
                if line<>"" and line[0]<>"#":
                    self.ignoredrepos.append(line.split("::")[0])            
        
        ignorefile=j.system.fs.joinPaths(self.accountPathLocal,".ignore") 
        if j.system.fs.exists(ignorefile):
            for line in j.system.fs.fileGetContents(ignorefile).split("\n"):
                line.strip().lower()
                if line<>"" and line[0]<>"#":
                    self.ignoredrepos.append(line.strip().lower())
        else:
            j.system.fs.writeFile(ignorefile,"#repos listed in this file will be ignored when doing a group action like push & pull. \n")
        activereposfile=j.system.fs.joinPaths(self.accountPathLocal,".active") 
        if j.system.fs.exists(activereposfile):
            for line in j.system.fs.fileGetContents(activereposfile).split("\n"):
                line.strip().lower()
                if line<>""  and line[0]<>"#":
                    self.activerepos.append(line)
                    if not j.system.fs.exists(j.system.fs.joinPaths(self.accountPathLocal,line)):
                        j.console.echo("Cannot find active repo with name %s from bitbucket account %s, will now try to clone" % (line,self.accountName))
                        url,login,passwd = self.bitbucket_client._accountGetLoginInfo(self.accountName)
                        if url[-1]<>"/":
                            url=url+"/"
                        repoName=line
                        cl=j.clients.mercurial.getclient("/opt/code/%s/%s/" % (self.accountName,repoName) ,"%s%s" % (url,repoName),branchname="")
                        self.bitbucketclients[repoName]=cl
                    
        if self.activerepos==[]:
            #empty list lets fill in with all available ones but commented
            reponames=self.getRepoNamesLocal(False,False)
            reponames.sort()
            out="#repos listed in this file will be the only ones looked at when doing a group action like push & pull. \n"
            for reponame in reponames:
                out+="#%s\n" % reponame
            j.system.fs.writeFile(activereposfile,out)
                
    def lastactionstatusSet(self,name,status):
        j.system.fs.writeFile(self.lastactionstatusFile,"%s::%s\n" % (name,status),append=True)
        
    def lastactionstatusClear(self):
        j.system.fs.remove(self.lastactionstatusFile)
        self._init()
                
                
    def checkRepoActive(self,name):
        """
        in /opt/code/$accountname/.active there can be names of repo's which should only be used when doing group actions like pull, push, ...
        """
        return name.strip().lower() in self.activerepos
    
    def checkRepoIgnored(self,name):
        """
        in /opt/code/$accountname/.ignore there can be names of repo's which should not be used when doing group actions like pull, push, ...
        """
        return name.strip().lower() in self.ignoredrepos    

    def addGroup(self, groupName):
        """
        Add Bitbucket new group

        @param groupName:       Bitbucket new group name
        @type groupName:        string
        @return The newly created Bitbucket L{Group}
        @rtype L{Group}
        @raise Exception in case of errors
        """
        self._validateValues(groupName=groupName, accountName=self.accountName)
        return self._callBitbucketRestAPI(BitbucketRESTCall.GROUPS, j.enumerators.RESTMethod.POST, uriParts=[self.accountName], data={'name': groupName})

    def addRepo(self, repoName,usersOwner=[]):
        """
        Add Bitbucket repo
        """
        accountConfig = self.bitbucket_client._accountGetConfig(self.accountName)
        cmd="curl -X POST -u %s:%s https://api.bitbucket.org/1.0/repositories/? -d name=%s -d scm=hg" % (accountConfig['login'],\
                                                                                                         accountConfig['passwd'],repoName)
        resultcode,content,object= self._execCurl(cmd)
        if resultcode>0:
            print "DEBUG NOW addrepo bitbucket"
        return object


    def deleteRepo(self, repoName):
        """
        delete Bitbucket repo
        """
        accountConfig = self.bitbucket_client._accountGetConfig(self.accountName)
        cmd="curl -X DELETE -u %s:%s https://api.bitbucket.org/1.0/repositories/%s/%s/" % \
            (accountConfig['login'],  accountConfig['passwd'],self.accountName,repoName)
        object=False
        if j.console.askYesNo("Are you sure you want to delete %s" % repoName):
            resultcode,content,object= self._execCurl(cmd)
            if resultcode>0:
                from JumpScale.core.Shell import ipshell
                print "DEBUG NOW delete bitbucket"
                ipshell()
                return object
        return object


    def getRepoInfo(self,repoName):
        """
        """
        accountConfig = self.bitbucket_client._accountGetConfig(self.accountName)
        cmd="curl -X GET -u %s:%s https://api.bitbucket.org/1.0/repositories/%s/%s/" % \
            (accountConfig['login'],  accountConfig['passwd'],self.accountName,repoName)
        resultcode,content,object= self._execCurl(cmd)
        return object

    def _execCurl(self,cmd):        
        resultTmpfile = j.system.fs.joinPaths(j.dirs.tmpDir, j.base.idgenerator.generateGUID())
        cmd+=" > %s" % resultTmpfile 
        resultcode, content = j.system.process.execute(cmd, False, True)
        content = j.system.fs.fileGetContents(resultTmpfile )
        j.system.fs.remove(resultTmpfile)
        if resultcode > 0:
            j.errorconditionhandler.raiseError("Cannot addrepo. Cannot execute \n%s" %cmd)
        try:
            object = json.loads(content) if content else dict()
        except:
            object=None
        return resultcode,content,object

#    def _getAccountPathLocal(self,accountName):
#        return j.system.fs.joinPaths(self.codedir,"bitbucket_%s"%accountName)

    def getRepoPathLocal(self,repoName="",die=True):      
        if repoName=="":
            repoName=j.gui.dialog.askChoice("Select repo",self.getRepoNamesLocal())
            if repoName==None:
                if die:
                    raise RuntimeError("Cannot find repo for accountName %s" % self.accountName)
                else:
                    return ""
        path=j.system.fs.joinPaths(self.accountPathLocal,repoName)
        j.system.fs.createDir(path)
        return path


    ##REVIEW codemgmt1 :all P1 
    def getRepoNamesLocal(self,checkIgnore=True,checkactive=True):
        if j.system.fs.exists(self.accountPathLocal):
            items=j.system.fs.listDirsInDir(self.accountPathLocal,False,True)
            if checkactive and len(self.activerepos)<>0:
                items=[item for item in items if self.checkRepoActive(item)]                 
            if checkIgnore:
                items=[item for item in items if not self.checkRepoIgnored(item)]                 
            return items        
        else:
            return []
        ##REVIEW-END

    def getRepoPathRemote(self,repoName=""):
        url,login,passwd=self.bitbucket_client.accountGetLoginInfo(self.accountName)
        if repoName=="":
            repoName=j.gui.dialog.askChoice("Select repo from bitbucket",self.getRepoNamesFromBitbucket())
        return "%s%s".strip() % (url,repoName)

    def _callBitbucketRestAPI(self, call, method="GET", uriParts=None, params=None, data=None):
        """
        Make a call to one of the Bitbucket REST API(s)

        @param call:            Bitbucket REST call to make
        @type call:             L{BitbucketRESTCall}
        @param method:          REST method used to initiate the call
        @type method:           string defining e.g. get
        @param uriParts:        Addtional parts to be added to the URI
        @type uriParts:         list
        @param params:          Optional params to be sent URL encoded in the REST request URI
        @type params:           dict
        @param data:            Optional data to be sent through the call
        @type data:             list or dict
        @return A deserialized result from JSON to its Python represemtation
        @raise Exception in case of errors
        """
        # TODO - MNour: Think about a generic REST client that can be configured and used from different components.
        # url, login, passwd = self.accountGetLoginInfo(accountName)
        #http=j.clients.http.getconnection()
        #http.addAuthentication(login,passwd)
        #url="https://api.bitbucket.org/1.0/users/%s/" % self._getBitbucketUsernameFromUrl(url)
        #content=http.get(url)
        # TODO - KDS: Need a better way than curl, the authentication doesnt seem to work when using the http jumpscale extension.
        j.system.platformtype.ubuntu.checkInstall("curl","curl")
        resultTmpfile = j.system.fs.joinPaths(j.dirs.tmpDir, j.base.idgenerator.generateGUID())
        headerTmpfile = j.system.fs.joinPaths(j.dirs.tmpDir, j.base.idgenerator.generateGUID())
        accountConfig = self.bitbucket_client._accountGetConfig(self.accountName)
        uriPartsString = '%s/' %'/'.join(uriParts) if uriParts else ''
        parameters = params if params else dict()
        #parameters['format'] = self.bitbucket_client.resultFormat

        dataString = ''
        if data:
            if type(data) is list:
                dataString = ','.join(data)
            elif type(data) is dict:
                dataString = urllib.urlencode(data)
            else:
                j.errorconditionhandler.raiseError("Invalid data type '%s', data value is '%s'." %(type(data), data))

        #cmd = "curl --dump-header %(headerTmpfile)s --user %(login)s:%(password)s --request %(method)s '%(apiURI)s/%(apiVersion)s/%(call)s/%(uriParts)s?%(parameters)s' --data '%(data)s' > %(resultTmpfile)s" \
            #%{'headerTmpfile': headerTmpfile,
                #'login': accountConfig['login'], 
                #'password': accountConfig['passwd'], 
                #'call': call, 
                #'resultTmpfile': resultTmpfile, 
                #'apiURI': self.bitbucket_client.apiURI,
                #'apiVersion': self.bitbucket_client.apiVersion, 
                #'method': method, 
                #'data': dataString, 
                #'uriParts': uriPartsString, 
                #'parameters': urllib.urlencode(parameters)}

        cmd = "curl -X %(method)s --user %(login)s:%(password)s  '%(apiURI)s/%(apiVersion)s/%(call)s/%(uriParts)s" %{\
            'method':method,
            'login': accountConfig['login'], 
            'password': accountConfig['passwd'], 
            'call': call, 
            'apiURI': self.bitbucket_client.apiURI,
            'apiVersion': self.bitbucket_client.apiVersion, 
            'uriParts': uriPartsString }

        if parameters<>"":
            cmd+="?%s" % urllib.urlencode(parameters)            

        cmd+="'"

        if dataString<>"":            
            cmd+=" --data '%s' " % dataString

        cmd+=" > %s" % resultTmpfile        

        resultcode, content = j.system.process.execute(cmd, False, True)
        if resultcode > 0:
            j.errorconditionhandler.raiseError("Cannot get reponames from repo. Cannot execute %s" %cmd)

        # TODO - MNour: Add error checking and handling.
        content = j.system.fs.fileGetContents(resultTmpfile )
        j.system.fs.remove(resultTmpfile)
        #j.system.fs.remove(headerTmpfile)

        try:
            object = json.loads(content) if content else dict()
        except:
            j.errorconditionhandler.raiseError("Cannot call rest api of bitbucket, call was %s" %cmd)

        # TODO - MNour: Do we need to construct Bitbucket resources classes out of json deserialized object ?
        return object

    def _getBitbucketRepoInfo(self):
        return self._callBitbucketRestAPI(BitbucketRESTCall.USERS, uriParts=[self.accountName])

    def findRepoFromBitbucket(self,partofName="",reload=False):
        """
        will use bbitbucket api to retrieven all repo information
        @param reload means reload from bitbucket   
        """
        names=self.getRepoNamesFromBitbucket(partofName,reload)
        j.gui.dialog.message("Select bitbucket repository")
        reposFound2=j.gui.dialog.askChoice("",names)        
        return reposFound2

    def getRepoNamesFromBitbucket(self,partOfRepoName="",reload=False):
        """
        will use bbitbucket api to retrieven all repo information
        @param reload means reload from bitbucket   
        """
        if self.bitbucket_client.accountsRemoteRepoNames.has_key(self.accountName) and reload==False:
            repoNames= self.bitbucket_client.accountsRemoteRepoNames[self.accountName]
        else:
            repos=self._getBitbucketRepoInfo()
            repoNames=[str(repo["slug"]) for repo in repos["repositories"]] 
            self.bitbucket_client.accountsRemoteRepoNames[self.accountName]=repoNames
        if partOfRepoName<>"":
            partOfRepoName=partOfRepoName.replace("*","").replace("?","").lower()
            repoNames2=[]
            for name in repoNames:
                name2=name.lower()
                if name2.find(partOfRepoName)<>-1:
                    repoNames2.append(name)            
                #print name2 + " " + partOfRepoName + " " + str(name2.find(partOfRepoName))
            repoNames=repoNames2


        return repoNames

    def getMercurialClient(self,repoName="",branch=None):
        """
        """
        #if self.bitbucketclients.has_key(repoName):
            #return self.bitbucketclients[repoName]
        #@todo P2 cache the connections but also use branchnames
        
        self.bitbucket_client._init()

        if repoName=="":
            repoName=self.findRepoFromBitbucket(repoName)       
        if repoName=="":
            raise RuntimeError("reponame cannot be empty")
        url,login,passwd = self.bitbucket_client._accountGetLoginInfo(self.accountName)
        
        if url[-1]<>"/":
            url=url+"/"
            
        url+="%s/"%repoName
            
        hgrcpath=j.system.fs.joinPaths(self.getRepoPathLocal(repoName),".hg","hgrc")
        if j.system.fs.exists(hgrcpath):
            editor=j.codetools.getTextFileEditor(hgrcpath)
            editor.replace1Line("default=%s" % url,["default *=.*"])
        
        j.clients.bitbucket.log("try to init mercurial client:%s on path:%s"%(repoName,self.getRepoPathLocal(repoName)),category="getclient")
        cl = j.clients.mercurial.getClient("%s/%s/%s/" % (j.dirs.codeDir,self.accountName,repoName), url, branchname=branch)
        j.clients.bitbucket.log("mercurial client inited for repo:%s"%repoName,category="getclient")
        self.bitbucketclients[repoName]=cl
        return cl

    def status(self,repoName="",checkIgnore=True):
        """
        ask for status of repo, see all changes
        @param if reponame=="" then do all
        """
        if repoName<>"":
            reponames=[repoName]
        else:
            reponames=self.getRepoNamesLocal(checkIgnore=checkIgnore)           
       
        pagepos=0
        def pprint(reponame,status,mods,pagepos):
            if len(mods)>0:
                pagepos+=1
                j.console.echo("%s : %s" % (reponame,status.upper()))
                if pagepos>50 and j.application.shellconfig.interactive:
                    j.console.askString("Next page, press enter")
                    pagepos=0
                for mod in mods:
                    if pagepos>50 and j.application.shellconfig.interactive:
                        j.console.askString("Next page, press enter")
                        pagepos=0
                    pagepos+=1
                    j.console.echo(" %s" % mod)
                j.console.echo("\n")
                pagepos+=2
            return pagepos
                       
        for repoName in reponames:
            cl=self.getMercurialClient(repoName)
            mods=cl.getModifiedFiles()
            for status in ["added","modified","missing","removed","nottracked","ignored"]:
                pagepos=pprint(repoName,status,mods[status],pagepos)
            
    def pullFromBitbucket(self,all=False,force=True,excludes=[],ignoreFailures=False):
        errors=[]
        if all:
            names=self.getRepoNamesFromBitbucket()
        else:
            names=j.console.askChoiceMultiple(self.getRepoNamesFromBitbucket(),"select repo's",True)
        
        for name in names:
            match=False
            if excludes<>[]:                
                for exclude in excludes:
                    if name.find(exclude)<>-1:
                        match=True
            if excludes==[] or not match :
                if ignoreFailures:
                    try:
                        self.pull(name,checkIgnore=False,force=force)
                    except Exception,e:                        
                        if str(e).find("NOT IMPLEMENTED"):
                            errors.append(["not mercurial type repo",self.accountName,name])
                            j.system.fs.removeDirTree(j.system.fs.joinPaths(self.accountPathLocal,name))
                        else:
                            errors.append([str(e),self.accountName,name])                        
                        j.console.echo( "ERROR: %s" % name)                        
                else:
                    self.pull(name,checkIgnore=False,force=force)
        return errors

    def pull(self,repoName="",message="",update=True,merge=True,checkIgnore=True,force=False,branch="default"):
        """
        pull repo to local location
        @param if reponame=="" then checkout all
        @param update if update will update local repo
        @param merge if merge will try an merge local repo
        @param checkIgnore this will check the ignore file to ignore certain repo's when doing this action
        @param force if update=True & force=True then repo will update and all local changes will be overwritten
        """
        if repoName<>"":
            reponames=[repoName]
        else:
            reponames=self.getRepoNamesLocal(checkIgnore=checkIgnore)
        
        for repoName in reponames:
            cl=self.getMercurialClient(repoName,branch=branch)
            j.console.echo("* pull %s" % repoName)
            
            cl.pull()
            
            if force:
                update=True
                merge=False
                
            if update and merge:
                cl.updatemerge(commitMessage=message\
                                ,ignorechanges=False,addRemoveUntrackedFiles=True,trymerge=True,pull=False)
            elif update and not merge:
                cl.update(die=True,force=force)
                
            else:
                raise RuntimeError("Could not pull %s" % repoName)

            self.lastactionstatusSet(repoName,"PULL DONE")
        self.lastactionstatusClear()
            
    def push(self, repoName="", message="", commit=True, addremove=True,
            checkIgnore=True, pull=False, user=None):
        """
        push local repo to remote repo

        if reponame=="" then push all

        @param commit before pushing will commit
        @param addremove before pushing will addremove        
        @param user: optional user identification string to use in a possible mercurial commit
        @type user: string
        """
        
        if not commit and addremove:
            raise RuntimeError("Do not support to addremove files without committing")
        #if commit or addremove:
            #self.commit(message=message,addremove=addremove)   
        #@todo code needs to be verified and made better
        if repoName<>"":
            reponames=[repoName]
        else:
            reponames=self.getRepoNamesLocal(checkIgnore=checkIgnore)
        
        for repoName in reponames:
            cl=self.getMercurialClient(repoName)
            if pull:
                j.console.echo("* commit push pull %s" % repoName)
            else:
                j.console.echo("* commit push %s" % repoName)
            cl.commitpush(commitMessage=message, ignorechanges=False,
                    addRemoveUntrackedFiles=addremove, trymerge=True, pull=pull,
                    user=user)
            self.lastactionstatusSet(repoName,"PUSH DONE")
        self.lastactionstatusClear()

    def checkoutForceUpdateRepo(self,repoName=""):
        """
        pull & update repo to local location
        """
        cl=self.getMercurialClient(repoName)
        return cl.pullupdate(force=True)


    def getGroups(self):
        """
        Retrieve all Bitbucket groups for the given account.

        @return List of Bitbucket groups
        @rtype list
        @raise Exception in case of errors
        """
        # TODO - MNour: Objectization of returned values.
        self._validateValues(accountName=self.accountName)
        return self._callBitbucketRestAPI(BitbucketRESTCall.GROUPS, uriParts=[self.accountName])

    def getGroup(self, groupName):
        """
        Retrieve a Bitbucket group that has the same exact specified group name

        @param groupName:       Bitbucket group name
        @type groupName:        string
        @return Bitbucket L{Group}
        @rtype L{Group}
        @raise Exception in case of errors
        """
        self._validateValues(groupName=groupName, accountName=self.accountName)
        groups = [group for group in self.getGroups() if group['name'] == groupName]#self.getGroups(self.accountName)
        if not groups:
            j.errorconditionhandler.raiseError('No group found with name [%s].' %groupName)

        return groups[0] if len(groups) == 1 else j.errorconditionhandler.raiseError('Found more than group with name [%s].' %groupName)

    ## TODO - MNour: Implement this method
    #def findGroup(self, regex):
        #"""
        #Find Bitbucket group which matches the specified regular expression

        #@param regex:       Regular expression using using which to match group names
        #@type regex:        string
        #@return List of Bitbucket L{Groups}
        #@rtype list
        #@raise Exception in case of errors
        #"""
        #self._validateValues(accountName=self.accountName)
        #j.errorconditionhandler.raiseError('Method not yet implemented.')



    #def getRepoNamesRemote(self):
        #"""
        #Retrieve all Bitbucket repositories which can be access by the account specified

        #@return List of Bitbucket L{Repository}(s), or empty list of not repositories accessed by the specified account
        #@rtype list
        #@raise Exception in case of errors
        #"""
        #self._validateValues(accountName=self.accountName)
        #return self._callBitbucketRestAPI(BitbucketRESTCall.USER, uriParts=[str(BitbucketRESTCall.REPOSITORIES)])

    #def checkRepoRemote(self, repoName):
        #"""
        #Check for the existence of a Bitbucket repository

        #@param repoName:        Bitbucket repository name
        #@type repoName:         string
        #@return True if the Bitbucket repository exists, False otherwise
        #@rtype Boolean
        #@raise Exception in case of error
        #"""
        #self._validateValues(repoName=repoName, accountName=self.accountName)
        #return len([repo for repo in self.getRepoNamesRemote() if repo['name'] == repoName]) > 0

    def checkGroup(self, groupName):
        """
        Check whether group exists or not

        @param groupName:       Bitbucket group to lookup if exists
        @type groupName:        string
        @return True if group exists, False otherwise
        """
        self._validateValues(groupName=groupName, accountName=self.accountName)
        return len([group for group in self.getGroups() if group['name'] == groupName]) > 0

    def deleteGroup(self, groupName):
        """
        Delete the specified Bitbucket group

        @param groupName:       Bitbucket group name
        @type groupName:        string
        @raise Exception in case of errors
        """
        self._validateValues(groupName=groupName, accountName=self.accountName)
        groupSlug = self._getGroupSlug(groupName)
        self._callBitbucketRestAPI(BitbucketRESTCall.GROUPS, "delete", uriParts=[self.accountName, groupSlug])

    def getGroupMembers(self, groupName):
        """
        Retrieve Bitbucket group members

        @param groupName:       Bitbucket group name
        @type groupName:        string
        @return Bitbucket group members, empty if no members exist
        @rtype list
        @raise Exception in case of errors
        """
        self._validateValues(groupName=groupName, accountName=self.accountName)
        groupSlug = self._getGroupSlug(groupName)
        return [member['username'] for member in self._callBitbucketRestAPI(BitbucketRESTCall.GROUPS, uriParts=[self.accountName, groupSlug, 'members'])]

    def addGroupMember(self, memberLogin, groupName):
        """
        Add a new member to a Bitbucket group

        @param memberLogin:     Bitbucket member login
        @type memberLogin:      string
        @param groupName:       Bitbucket group name
        @type groupName:        string
        @return The L{Member} if it has been added successfully
        @rtype L{Member}
        @raise Exception in case of errors
        """
        self._validateValues(memberLogin=memberLogin, groupName=groupName, accountName=self.accountName)
        groupSlug = self._getGroupSlug(groupName)
        return self._callBitbucketRestAPI(BitbucketRESTCall.GROUPS, "put", uriParts=[self.accountName, groupSlug, 'members', memberLogin])

    def updateGroup(self, groupName, **kwargs):
        """
        Update Bitbucket group settings

        @param groupName:       Bitbucket group name
        @type groupName:        string
        @param kwargs:          Bitbucket group setteings required to be updated\
        @type kwargs:           dict
        @return The L{Group} after update if update has been done successfully
        @rtype L{Group}
        @raise Exception in case of errors
        """
        self._validateValues(groupName=groupName, accountName=self.accountName)
        group = self.getGroup(groupName)
        if kwargs:
            if not str(BitbucketSettingsParam.NAME) in kwargs:
                kwargs[str(BitbucketSettingsParam.NAME)] = group[str(BitbucketSettingsParam.NAME)]

            if not BitbucketSettingsParam.PERMISSION in kwargs:
                kwargs[str(BitbucketSettingsParam.PERMISSION)] = group[str(BitbucketSettingsParam.PERMISSION)]

        return self._callBitbucketRestAPI(BitbucketRESTCall.GROUPS, "get", [group['slug']], **kwargs)

    def deleteGroupMember(self, memberLogin, groupName):
        """
        Delete a member from a Bitbucket group

        @param memberLogin:     Bitbucket member login
        @type memberLogin:      string
        @param groupName:       Bitbucket group name
        @type groupName:        string
        @raise Exception in case of errors
        """
        self._validateValues(memberLogin=memberLogin, groupName=groupName, accountName=self.accountName)
        groupSlug = self._getGroupSlug(groupName)
        self._callBitbucketRestAPI(BitbucketRESTCall.GROUPS, "get", uriParts=[self.accountName, groupSlug, 'members', memberLogin])

    def getGroupPrivileges(self, filter=None, private=None):
        """
        Retrieve all group privileges specified by that Bitbucket account

        @param filter:          Filtering the permissions of privileges we are looking for
        @type filter:           L{BitbucketPermission}
        @param private:         Defines whether to retrieve privileges defined on private repositories or not
        @type private:          boolean
        @return All L{Privilege}s specified by that Bitbucket account name
        @rtype list
        @raise Exception in case of errors
        """
        self._validateValues(accountName=self.accountName)
        params = dict()
        if filter:
            params['filter'] = filter

        if private != None:
            params['private'] = private

        return self._callBitbucketRestAPI(BitbucketRESTCall.GROUP_PRIVILEGES.value, uriParts=[self.accountName], params=params)

    def getRepoGroupPrivileges(self, repoName):
        """
        Retrieve all group privileges specified by that Bitbucket account on that Bitbucket repository

        @param repoName:        Bitbucket repository name
        @type repoName:         string
        @return All L{Privilege}s specified by that Bitbucket account name on that Bitbucket repository
        @rtype list
        @raise Exception in case of errors
        """
        self._validateValues(repoName=repoName, accountName=self.accountName)
        return self._callBitbucketRestAPI(BitbucketRESTCall.GROUP_PRIVILEGES.value, uriParts=[self.accountName, repoName])

    def grantGroupPrivileges(self, groupName, repoName, privilege):
        """
        Grant a group privilege to the specified Bitbucket repository

        @param groupName:       Bitbucket group name
        @type groupName:        string
        @param repoName:        Bitbucket repository
        @type repoName:         string
        @param privilege:       Group privilege
        @type privilege:        L{BitbucketPermission}
        @return List L{Privilege}s granted to the specified repository
        @rtype list
        @raise Exception in case of errors
        """
        self._validateValues(groupName=groupName, repoName=repoName, accountName=self.accountName)
        groupSlug = self._getGroupSlug(groupName)
        return self._callBitbucketRestAPI(BitbucketRESTCall.GROUP_PRIVILEGES.value, "get",
                                          uriParts=[self.accountName, repoName, self.accountName, groupSlug], data=[str(privilege)])

    def revokeRepoGroupPrivileges(self, groupName, repoName):
        """
        Revoke group privileges on the defined Bitbucket repository

        @param groupName:       Bitbucket group name
        @type groupName:        string
        @param repoName:        Bitbucket repository name
        @type repoName:         string
        @raise Exception in case of errors
        """
        self._validateValues(groupName=groupName, repoName=repoName, accountName=self.accountName)
        groupSlug = self._getGroupSlug(groupName)
        self._callBitbucketRestAPI(BitbucketRESTCall.GROUP_PRIVILEGES.value, "get",
                                   uriParts=[self.accountName, repoName, self.accountName, groupSlug])

    def revokeGroupPrivileges(self, groupName):
        """
        Revoke all group privileges

        @param groupName:       Bitbucket group name
        @type groupName:        string
        @param repoName:        Bitbucket repository name
        @type repoName:         string
        @raise Exception in case of errors
        """
        self._validateValues(groupName=groupName, accountName=self.accountName)
        groupSlug = self._getGroupSlug(groupName)
        self._callBitbucketRestAPI(BitbucketRESTCall.GROUP_PRIVILEGES.value, "get",
                                   uriParts=[self.accountName, self.accountName, groupSlug])

    def _getGroupSlug(self, groupName):
        """
        Retriev Bitbucket group slug name

        @param groupName:       Bitbucket group name
        @type groupName:        string
        @return Bitbucket group slug name or Exception in case of errors
        @rtype string
        """
        self._validateValues(groupName=groupName, accountName=self.accountName)
        group = self.getGroup(groupName)
        return group['slug']

    def _validateValues(self, **kwargs):
        """
        Validate values that they are not neither None nor empty valued

        @param kwargs:          Values to be validated
        @type kwargs:           dict
        @raise Exception in case one or more values do not satisfy the conditions specified above
        """
        invalidValues = dict()
        for key in kwargs:
            if not kwargs[key]:
                invalidValues[key] = kwargs[key]

        if invalidValues:
            j.errorconditionhandler.raiseError('Invalid values: %s' %invalidValues)


    def exportRepo(self,name, branch, codeDir = '/opt/code3'):
        source = j.system.fs.joinPaths(j.dirs.codeDir, self.accountName, name)
        destination = j.system.fs.joinPaths(codeDir, self.accountName, name, branch)
        j.system.fs.copyDirTree(source, destination)      
        return destination
    
    def exportAllFromJpackages(self, allVersions=False, qualityLevels=[], codeDir = '/opt/code'):
        scanner = j.packages.getJPackageMetadataScanner()
        scanner.scan(allVersions, qualityLevels)
        repos = []
        for item in scanner.getRecipeItemsAsLists():
            jpname = item[1]
            branch = item[3]
            if not [jpname, branch] in repos:
                repos.append([jpname, branch])
        for repo in repos:
            exportRepo(repo[0], repo[1], codeDir)
 
