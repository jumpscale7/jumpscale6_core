import json
from JumpScale import j
from JumpScale.core.baseclasses import BaseEnumeration

from BitbucketConfigManagement import *
import urllib

import requests
from requests.auth import HTTPBasicAuth
import os


class Bitbucket:
    """
    Bitbucket client enables administrators and developers leveraging Bitbucket services through JumpScale
    """

    def __init__(self):
        self.config=BitbucketConfigManagement()
        self.connections={}
        j.logger.consolelogCategories.append("bitbucket")

        hgpath = '{0}/.hgrc'.format(os.getenv('HOME'))
        if j.system.fs.exists(hgpath):
            C=j.system.fs.fileGetContents(hgpath)
        else:
            C=''
        if C.find("[hostfingerprints]")==-1:
            C+="\n[hostfingerprints]\nbitbucket.org =24:9c:45:8b:9c:aa:ba:55:4e:01:6d:58:ff:e4:28:7d:2a:14:ae:3b\n"
            j.system.fs.writeFile(hgpath,C)

    def getRepoInfo(self, accountName, repoName):
        url = "https://bitbucket.org/api/1.0/repositories/%s/%s" % (accountName, repoName)
        result = requests.get(url)
        if result.ok:
            return result.json()
        else:
            return result.status_code

    def log(self,msg,category="",level=5):
        category="bitbucket.%s"%category
        category=category.rstrip(".")
        j.logger.log(msg,category=category,level=level)

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

    def getBitbucketRepoClient(self, accountName, repoName, branch='default'):
        url, accountLogin, accountPasswd = self._getRepoInfo(accountName, repoName, branch)
        if self.connections.has_key(accountName):
            return self.connections[accountName]
        self.connections[accountName] = BitbucketConnection(accountName,url,login=accountLogin,passwd=accountPasswd)
        return self.connections[accountName]

    def _getRepoInfo(self, accountName, repoName, branch="default"):
        loginInfo = ''
        login = None
        passwd = None
        repoInfo = self.getRepoInfo(accountName, repoName)

        config = self._accountGetConfig(accountName)
        login = config["login"]
        passwd = config["passwd"]

        if login.find("@login")<>-1 or login.strip()=="":
            if j.application.shellconfig.interactive:
                login=j.gui.dialog.askString("  \nLogin for bitbucket account %s" % accountName)
            else:
                login = ""
            self.config.configure(accountName,{'login': login})
        
        if passwd.find("@passwd")<>-1 or passwd.strip()=="":
            if j.application.shellconfig.interactive:
                passwd = j.gui.dialog.askPassword("  \nPassword for bitbucket account %s" % accountName, confirm=False)
            else:
                passwd = ""
            self.config.configure(accountName,{'passwd': passwd})
        if j.application.shellconfig.interactive and (login=="" or passwd==""):
            self.accountsReview(accountName)
        loginInfo = '%s:%s@' % (login, passwd)

        if repoInfo == 404: #not found
            j.errorconditionhandler.raiseOperationalCritical("Repo %s/%s is invalid" % (accountName, repoName))
        # elif repoInfo == 403: #forbidden
            
        if login not in ('hg', 'ssh'):
            url = " https://%sbitbucket.org/%s/" % (loginInfo, accountName)
        else:
            url=" ssh://hg@bitbucket.org/%s/" % (accountName)
        if login==None or login.strip()=="":
            raise RuntimeError("Login cannot be empty, url:%s"%url)

        return url, login, passwd

    def getMecurialRepoClient(self, accountName, reponame,branch="default"):
        bitbucket_connection = self.getBitbucketRepoClient(accountName, reponame)
        return bitbucket_connection.getMercurialClient(reponame,branch=branch)


class BitbucketConnection(object):

    def __init__(self, accountName,url,login,passwd):
        self.accountName = accountName
        self.url=url
        self.login=login
        self.passwd=passwd
        self.accountPathLocal = j.system.fs.joinPaths("/opt/code",accountName)
        j.system.fs.createDir(self.accountPathLocal)
        self.mercurialclients={}

    def restCallBitbucket(self,url):
        url="https://bitbucket.org/api/1.0/%s"%url
        r=requests.get(url, auth=HTTPBasicAuth(self.login, self.passwd))
        try:
            data=r.json()
        except Exception,e:
            msg="Could not connect to:%s, reason:%s, login was:'%s'"%(url,r.reason,self.login)
            raise RuntimeError(msg)
        return data
            

    def addGroup(self, groupName):
        """
        Add Bitbucket new group

        @param groupName:       Bitbucket new group name
        @return The newly created Bitbucket L{Group}
        """
        raise RuntimeError("not implemented")

    def addRepo(self, repoName,usersOwner=[]):
        """
        Add Bitbucket repo
        """
        raise RuntimeError("not implemented")

    def deleteRepo(self, repoName):
        """
        delete Bitbucket repo
        """
        raise RuntimeError("not implemented")
        if j.console.askYesNo("Are you sure you want to delete %s" % repoName):
            resultcode,content,object= self._execCurl(cmd)
            if resultcode>0:
                from JumpScale.core.Shell import ipshell
                print "DEBUG NOW delete bitbucket"
                ipshell()
                return object
        return object

    def getChangeSets(self,reponame,limit=50):
        url="repositories/%s/%s/changesets/?limit=%s"%(self.accountName,reponame,limit)
        return self.restCallBitbucket(url)


    def getAccountInfo(self, accountName):
        url = "https://bitbucket.org/api/1.0/users/%s" % accountName
        result = requests.get(url)
        return result.ok

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

    def getRepoNamesLocal(self,checkIgnore=True,checkactive=True):
        if j.system.fs.exists(self.accountPathLocal):
            items=j.system.fs.listDirsInDir(self.accountPathLocal,False,True)
            return items
        else:
            return []

    def getRepoPathRemote(self,repoName=""):
        raise RuntimeError("not implemented")

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
        #if self.mercurialclients.has_key(repoName):
            #return self.mercurialclients[repoName]
        #@todo P2 cache the connections but also use branchnames

        if repoName=="":
            repoName=self.findRepoFromBitbucket(repoName)
        if repoName=="":
            raise RuntimeError("reponame cannot be empty")

        url = self.url
        if url[-1]<>"/":
            url=url+"/"

        url += "%s/"%repoName

        hgrcpath=j.system.fs.joinPaths(self.getRepoPathLocal(repoName),".hg","hgrc")
        if j.system.fs.exists(hgrcpath):
            editor=j.codetools.getTextFileEditor(hgrcpath)
            editor.replace1Line("default=%s" % url,["default *=.*"])
        j.clients.bitbucket.log("init mercurial client ##%s## on path:%s"%(repoName,self.getRepoPathLocal(repoName)),category="getclient")
        cl = j.clients.mercurial.getClient("%s/%s/%s/" % (j.dirs.codeDir,self.accountName,repoName), url, branchname=branch)
        # j.clients.bitbucket.log("mercurial client inited for repo:%s"%repoName,category="getclient")
        self.mercurialclients[repoName]=cl
        return cl



    def getGroups(self):
        """
        Retrieve all Bitbucket groups for the given account.
        @return List of Bitbucket groups
        """
        raise RuntimeError("not implemented")

    def getGroup(self, groupName):
        """
        Retrieve a Bitbucket group that has the same exact specified group name

        @param groupName:       Bitbucket group name
        @return Bitbucket L{Group}
        """
        raise RuntimeError("not implemented")
        self._validateValues(groupName=groupName, accountName=self.accountName)
        groups = [group for group in self.getGroups() if group['name'] == groupName]#self.getGroups(self.accountName)
        if not groups:
            j.errorconditionhandler.raiseError('No group found with name [%s].' %groupName)

        return groups[0] if len(groups) == 1 else j.errorconditionhandler.raiseError('Found more than group with name [%s].' %groupName)


    def checkGroup(self, groupName):
        """
        Check whether group exists or not

        @param groupName:       Bitbucket group to lookup if exists
        @return True if group exists, False otherwise
        """
        raise RuntimeError("not implemented")
        self._validateValues(groupName=groupName, accountName=self.accountName)
        return len([group for group in self.getGroups() if group['name'] == groupName]) > 0

    def deleteGroup(self, groupName):
        """
        Delete the specified Bitbucket group
        @param groupName:       Bitbucket group name
        """
        raise RuntimeError("not implemented")
        self._validateValues(groupName=groupName, accountName=self.accountName)
        groupSlug = self._getGroupSlug(groupName)
        self._callBitbucketRestAPI(BitbucketRESTCall.GROUPS, "delete", uriParts=[self.accountName, groupSlug])

    def getGroupMembers(self, groupName):
        """
        Retrieve Bitbucket group members

        @param groupName:       Bitbucket group name
        @return Bitbucket group members, empty if no members exist
        """
        raise RuntimeError("not implemented")
        self._validateValues(groupName=groupName, accountName=self.accountName)
        groupSlug = self._getGroupSlug(groupName)
        return [member['username'] for member in self._callBitbucketRestAPI(BitbucketRESTCall.GROUPS, uriParts=[self.accountName, groupSlug, 'members'])]

    def addGroupMember(self, memberLogin, groupName):
        """
        Add a new member to a Bitbucket group

        @param memberLogin:     Bitbucket member login
        @param groupName:       Bitbucket group name
        @return The L{Member} if it has been added successfully
        """
        raise RuntimeError("not implemented")
        self._validateValues(memberLogin=memberLogin, groupName=groupName, accountName=self.accountName)
        groupSlug = self._getGroupSlug(groupName)
        return self._callBitbucketRestAPI(BitbucketRESTCall.GROUPS, "put", uriParts=[self.accountName, groupSlug, 'members', memberLogin])

    def updateGroup(self, groupName, **kwargs):
        """
        Update Bitbucket group settings

        @param groupName:       Bitbucket group name
        @param kwargs:          Bitbucket group setteings required to be updated\
        @return The L{Group} after update if update has been done successfully
        """
        raise RuntimeError("not implemented")

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
        @param groupName:       Bitbucket group name
        """
        raise RuntimeError("not implemented")

        self._validateValues(memberLogin=memberLogin, groupName=groupName, accountName=self.accountName)
        groupSlug = self._getGroupSlug(groupName)
        self._callBitbucketRestAPI(BitbucketRESTCall.GROUPS, "get", uriParts=[self.accountName, groupSlug, 'members', memberLogin])

    def getGroupPrivileges(self, filter=None, private=None):
        """
        Retrieve all group privileges specified by that Bitbucket account

        @param filter:          Filtering the permissions of privileges we are looking for
        @param private:         Defines whether to retrieve privileges defined on private repositories or not
        @return All L{Privilege}s specified by that Bitbucket account name
        """
        raise RuntimeError("not implemented")
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
        @return All L{Privilege}s specified by that Bitbucket account name on that Bitbucket repository
        """
        raise RuntimeError("not implemented")
        self._validateValues(repoName=repoName, accountName=self.accountName)
        return self._callBitbucketRestAPI(BitbucketRESTCall.GROUP_PRIVILEGES.value, uriParts=[self.accountName, repoName])

    def grantGroupPrivileges(self, groupName, repoName, privilege):
        """
        Grant a group privilege to the specified Bitbucket repository

        @param groupName:       Bitbucket group name
        @param repoName:        Bitbucket repository
        @param privilege:       Group privilege
        @return List L{Privilege}s granted to the specified repository
        """
        raise RuntimeError("not implemented")

        self._validateValues(groupName=groupName, repoName=repoName, accountName=self.accountName)
        groupSlug = self._getGroupSlug(groupName)
        return self._callBitbucketRestAPI(BitbucketRESTCall.GROUP_PRIVILEGES.value, "get",
                                          uriParts=[self.accountName, repoName, self.accountName, groupSlug], data=[str(privilege)])

    def revokeRepoGroupPrivileges(self, groupName, repoName):
        """
        Revoke group privileges on the defined Bitbucket repository

        @param groupName:       Bitbucket group name
        @param repoName:        Bitbucket repository name
        """
        raise RuntimeError("not implemented")

        self._validateValues(groupName=groupName, repoName=repoName, accountName=self.accountName)
        groupSlug = self._getGroupSlug(groupName)
        self._callBitbucketRestAPI(BitbucketRESTCall.GROUP_PRIVILEGES.value, "get",
                                   uriParts=[self.accountName, repoName, self.accountName, groupSlug])

    def revokeGroupPrivileges(self, groupName):
        """
        Revoke all group privileges

        @param groupName:       Bitbucket group name
        @param repoName:        Bitbucket repository name
        """
        raise RuntimeError("not implemented")

        self._validateValues(groupName=groupName, accountName=self.accountName)
        groupSlug = self._getGroupSlug(groupName)
        self._callBitbucketRestAPI(BitbucketRESTCall.GROUP_PRIVILEGES.value, "get",
                                   uriParts=[self.accountName, self.accountName, groupSlug])

    def _getGroupSlug(self, groupName):
        """
        Retriev Bitbucket group slug name

        @param groupName:       Bitbucket group name
        @return Bitbucket group slug name or Exception in case of errors
        """
        raise RuntimeError("not implemented")

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


