import json
from JumpScale import j
from JumpScale.core.baseclasses import BaseEnumeration

from GitlabConfigManagement import *
# import urllib
# import requests
# from requests.auth import HTTPBasicAuth
import gitlab
import os

from gitlab import Gitlab

class GitlabInstance(Gitlab):

    def __init__(self, addr,login,passwd):
        self.addr=addr
        Gitlab.__init__(self,addr)
        # self.accountPathLocal = j.system.fs.joinPaths("/opt/code",accountName)
        # j.system.fs.createDir(self.accountPathLocal)
        # self._gitlab = gitlab.Gitlab(self.addr)
        self.login(login, passwd)
        # for item in dir(self._gitlab):
        #     if item[0]<>"_":
        #         setattr(self,item,getattr(self._gitlab,item))
        self.gitclients={}


    # def restCallGitlab(self,url):
    #     url="https://gitlab.org/api/1.0/%s"%url
    #     r=requests.get(url, auth=HTTPBasicAuth(self.login, self.passwd))
    #     try:
    #         data=r.json()
    #     except Exception,e:
    #         msg="Could not connect to:%s, reason:%s, login was:'%s'"%(url,r.reason,self.login)
    #         raise RuntimeError(msg)
    #     return data
            



    # def addGroup(self, groupName):
    #     """
    #     Add Gitlab new group

    #     @param groupName:       Gitlab new group name
    #     @return The newly created Gitlab L{Group}
    #     """
    #     raise RuntimeError("not implemented")

    # def addRepo(self, repoName,usersOwner=[]):
    #     """
    #     Add Gitlab repo
    #     """
    #     raise RuntimeError("not implemented")

    # def deleteRepo(self, repoName):
    #     """
    #     delete Gitlab repo
    #     """
    #     raise RuntimeError("not implemented")
    #     if j.console.askYesNo("Are you sure you want to delete %s" % repoName):
    #         resultcode,content,object= self._execCurl(cmd)
    #         if resultcode>0:
    #             from JumpScale.core.Shell import ipshell
    #             print "DEBUG NOW delete gitlab"
    #             ipshell()
    #             return object
    #     return object

    # def getChangeSets(self,reponame,limit=50):
    #     url="repositories/%s/%s/changesets/?limit=%s"%(self.accountName,reponame,limit)
    #     return self.restCallGitlab(url)


    # def getAccountInfo(self, accountName):
    #     url = "https://gitlab.org/api/1.0/users/%s" % accountName
    #     result = requests.get(url)
    #     return result.ok

    # def getRepoPathLocal(self,repoName="",die=True):
    #     if repoName=="":
    #         repoName=j.gui.dialog.askChoice("Select repo",self.getRepoNamesLocal())
    #         if repoName==None:
    #             if die:
    #                 raise RuntimeError("Cannot find repo for accountName %s" % self.accountName)
    #             else:
    #                 return ""
    #     path=j.system.fs.joinPaths(self.accountPathLocal,repoName)
    #     j.system.fs.createDir(path)
    #     return path

    # def getRepoNamesLocal(self,checkIgnore=True,checkactive=True):
    #     if j.system.fs.exists(self.accountPathLocal):
    #         items=j.system.fs.listDirsInDir(self.accountPathLocal,False,True)
    #         return items
    #     else:
    #         return []

    # def getRepoPathRemote(self,repoName=""):
    #     raise RuntimeError("not implemented")

    # def findRepoFromGitlab(self,partofName="",reload=False):
    #     """
    #     will use bgitlab api to retrieven all repo information
    #     @param reload means reload from gitlab
    #     """
    #     names=self.getRepoNamesFromGitlab(partofName,reload)
    #     j.gui.dialog.message("Select gitlab repository")
    #     reposFound2=j.gui.dialog.askChoice("",names)
    #     return reposFound2

    # def getRepoNamesFromGitlab(self,partOfRepoName="",reload=False):
    #     """
    #     will use bgitlab api to retrieven all repo information
    #     @param reload means reload from gitlab
    #     """
    #     if self.gitlab_client.accountsRemoteRepoNames.has_key(self.accountName) and reload==False:
    #         repoNames= self.gitlab_client.accountsRemoteRepoNames[self.accountName]
    #     else:
    #         repos=self._getGitlabRepoInfo()
    #         repoNames=[str(repo["slug"]) for repo in repos["repositories"]]
    #         self.gitlab_client.accountsRemoteRepoNames[self.accountName]=repoNames
    #     if partOfRepoName<>"":
    #         partOfRepoName=partOfRepoName.replace("*","").replace("?","").lower()
    #         repoNames2=[]
    #         for name in repoNames:
    #             name2=name.lower()
    #             if name2.find(partOfRepoName)<>-1:
    #                 repoNames2.append(name)
    #             #print name2 + " " + partOfRepoName + " " + str(name2.find(partOfRepoName))
    #         repoNames=repoNames2


    #     return repoNames

    # def getGitClient(self,repoName="",branch=None):
    #     """
    #     """
    #     #if self.gitclients.has_key(repoName):
    #         #return self.gitclients[repoName]
    #     #@todo P2 cache the connections but also use branchnames

    #     if repoName=="":
    #         repoName=self.findRepoFromGitlab(repoName)
    #     if repoName=="":
    #         raise RuntimeError("reponame cannot be empty")

    #     url = self.url
    #     if url[-1]<>"/":
    #         url=url+"/"

    #     url += "%s/"%repoName

    #     hgrcpath=j.system.fs.joinPaths(self.getRepoPathLocal(repoName),".hg","hgrc")
    #     if j.system.fs.exists(hgrcpath):
    #         editor=j.codetools.getTextFileEditor(hgrcpath)
    #         editor.replace1Line("default=%s" % url,["default *=.*"])
    #     j.clients.gitlab.log("init git client ##%s## on path:%s"%(repoName,self.getRepoPathLocal(repoName)),category="getclient")
    #     cl = j.clients.git.getClient(self.getCodeFolder(repoName), url, branchname=branch)
    #     # j.clients.gitlab.log("git client inited for repo:%s"%repoName,category="getclient")
    #     self.gitclients[repoName]=cl
    #     return cl

    # def getCodeFolder(self, repoName):
    #     return "%s/%s/%s/" % (j.dirs.codeDir,self.accountName,repoName)

    # def getGroups(self):
    #     """
    #     Retrieve all Gitlab groups for the given account.
    #     @return List of Gitlab groups
    #     """
    #     raise RuntimeError("not implemented")

    # def getGroup(self, groupName):
    #     """
    #     Retrieve a Gitlab group that has the same exact specified group name

    #     @param groupName:       Gitlab group name
    #     @return Gitlab L{Group}
    #     """
    #     raise RuntimeError("not implemented")
    #     self._validateValues(groupName=groupName, accountName=self.accountName)
    #     groups = [group for group in self.getGroups() if group['name'] == groupName]#self.getGroups(self.accountName)
    #     if not groups:
    #         j.errorconditionhandler.raiseError('No group found with name [%s].' %groupName)

    #     return groups[0] if len(groups) == 1 else j.errorconditionhandler.raiseError('Found more than group with name [%s].' %groupName)


    # def checkGroup(self, groupName):
    #     """
    #     Check whether group exists or not

    #     @param groupName:       Gitlab group to lookup if exists
    #     @return True if group exists, False otherwise
    #     """
    #     raise RuntimeError("not implemented")
    #     self._validateValues(groupName=groupName, accountName=self.accountName)
    #     return len([group for group in self.getGroups() if group['name'] == groupName]) > 0

    # def deleteGroup(self, groupName):
    #     """
    #     Delete the specified Gitlab group
    #     @param groupName:       Gitlab group name
    #     """
    #     raise RuntimeError("not implemented")
    #     self._validateValues(groupName=groupName, accountName=self.accountName)
    #     groupSlug = self._getGroupSlug(groupName)
    #     self._callGitlabRestAPI(GitlabRESTCall.GROUPS, "delete", uriParts=[self.accountName, groupSlug])

    # def getGroupMembers(self, groupName):
    #     """
    #     Retrieve Gitlab group members

    #     @param groupName:       Gitlab group name
    #     @return Gitlab group members, empty if no members exist
    #     """
    #     raise RuntimeError("not implemented")
    #     self._validateValues(groupName=groupName, accountName=self.accountName)
    #     groupSlug = self._getGroupSlug(groupName)
    #     return [member['username'] for member in self._callGitlabRestAPI(GitlabRESTCall.GROUPS, uriParts=[self.accountName, groupSlug, 'members'])]

    # def addGroupMember(self, memberLogin, groupName):
    #     """
    #     Add a new member to a Gitlab group

    #     @param memberLogin:     Gitlab member login
    #     @param groupName:       Gitlab group name
    #     @return The L{Member} if it has been added successfully
    #     """
    #     raise RuntimeError("not implemented")
    #     self._validateValues(memberLogin=memberLogin, groupName=groupName, accountName=self.accountName)
    #     groupSlug = self._getGroupSlug(groupName)
    #     return self._callGitlabRestAPI(GitlabRESTCall.GROUPS, "put", uriParts=[self.accountName, groupSlug, 'members', memberLogin])

    # def updateGroup(self, groupName, **kwargs):
    #     """
    #     Update Gitlab group settings

    #     @param groupName:       Gitlab group name
    #     @param kwargs:          Gitlab group setteings required to be updated\
    #     @return The L{Group} after update if update has been done successfully
    #     """
    #     raise RuntimeError("not implemented")

    #     self._validateValues(groupName=groupName, accountName=self.accountName)
    #     group = self.getGroup(groupName)
    #     if kwargs:
    #         if not str(GitlabSettingsParam.NAME) in kwargs:
    #             kwargs[str(GitlabSettingsParam.NAME)] = group[str(GitlabSettingsParam.NAME)]

    #         if not GitlabSettingsParam.PERMISSION in kwargs:
    #             kwargs[str(GitlabSettingsParam.PERMISSION)] = group[str(GitlabSettingsParam.PERMISSION)]

    #     return self._callGitlabRestAPI(GitlabRESTCall.GROUPS, "get", [group['slug']], **kwargs)

    # def deleteGroupMember(self, memberLogin, groupName):
    #     """
    #     Delete a member from a Gitlab group

    #     @param memberLogin:     Gitlab member login
    #     @param groupName:       Gitlab group name
    #     """
    #     raise RuntimeError("not implemented")

    #     self._validateValues(memberLogin=memberLogin, groupName=groupName, accountName=self.accountName)
    #     groupSlug = self._getGroupSlug(groupName)
    #     self._callGitlabRestAPI(GitlabRESTCall.GROUPS, "get", uriParts=[self.accountName, groupSlug, 'members', memberLogin])

    # def getGroupPrivileges(self, filter=None, private=None):
    #     """
    #     Retrieve all group privileges specified by that Gitlab account

    #     @param filter:          Filtering the permissions of privileges we are looking for
    #     @param private:         Defines whether to retrieve privileges defined on private repositories or not
    #     @return All L{Privilege}s specified by that Gitlab account name
    #     """
    #     raise RuntimeError("not implemented")
    #     self._validateValues(accountName=self.accountName)
    #     params = dict()
    #     if filter:
    #         params['filter'] = filter

    #     if private != None:
    #         params['private'] = private

    #     return self._callGitlabRestAPI(GitlabRESTCall.GROUP_PRIVILEGES.value, uriParts=[self.accountName], params=params)

    # def getRepoGroupPrivileges(self, repoName):
    #     """
    #     Retrieve all group privileges specified by that Gitlab account on that Gitlab repository

    #     @param repoName:        Gitlab repository name
    #     @return All L{Privilege}s specified by that Gitlab account name on that Gitlab repository
    #     """
    #     raise RuntimeError("not implemented")
    #     self._validateValues(repoName=repoName, accountName=self.accountName)
    #     return self._callGitlabRestAPI(GitlabRESTCall.GROUP_PRIVILEGES.value, uriParts=[self.accountName, repoName])

    # def grantGroupPrivileges(self, groupName, repoName, privilege):
    #     """
    #     Grant a group privilege to the specified Gitlab repository

    #     @param groupName:       Gitlab group name
    #     @param repoName:        Gitlab repository
    #     @param privilege:       Group privilege
    #     @return List L{Privilege}s granted to the specified repository
    #     """
    #     raise RuntimeError("not implemented")

    #     self._validateValues(groupName=groupName, repoName=repoName, accountName=self.accountName)
    #     groupSlug = self._getGroupSlug(groupName)
    #     return self._callGitlabRestAPI(GitlabRESTCall.GROUP_PRIVILEGES.value, "get",
    #                                       uriParts=[self.accountName, repoName, self.accountName, groupSlug], data=[str(privilege)])

    # def revokeRepoGroupPrivileges(self, groupName, repoName):
    #     """
    #     Revoke group privileges on the defined Gitlab repository

    #     @param groupName:       Gitlab group name
    #     @param repoName:        Gitlab repository name
    #     """
    #     raise RuntimeError("not implemented")

    #     self._validateValues(groupName=groupName, repoName=repoName, accountName=self.accountName)
    #     groupSlug = self._getGroupSlug(groupName)
    #     self._callGitlabRestAPI(GitlabRESTCall.GROUP_PRIVILEGES.value, "get",
    #                                uriParts=[self.accountName, repoName, self.accountName, groupSlug])

    # def revokeGroupPrivileges(self, groupName):
    #     """
    #     Revoke all group privileges

    #     @param groupName:       Gitlab group name
    #     @param repoName:        Gitlab repository name
    #     """
    #     raise RuntimeError("not implemented")

    #     self._validateValues(groupName=groupName, accountName=self.accountName)
    #     groupSlug = self._getGroupSlug(groupName)
    #     self._callGitlabRestAPI(GitlabRESTCall.GROUP_PRIVILEGES.value, "get",
    #                                uriParts=[self.accountName, self.accountName, groupSlug])

    # # def _getGroupSlug(self, groupName):
    # #     """
    # #     Retriev Gitlab group slug name

    # #     @param groupName:       Gitlab group name
    # #     @return Gitlab group slug name or Exception in case of errors
    # #     """
    # #     raise RuntimeError("not implemented")

    # #     self._validateValues(groupName=groupName, accountName=self.accountName)
    # #     group = self.getGroup(groupName)
    # #     return group['slug']

    # # def _validateValues(self, **kwargs):
    # #     """
    # #     Validate values that they are not neither None nor empty valued

    # #     @param kwargs:          Values to be validated
    # #     @type kwargs:           dict
    # #     @raise Exception in case one or more values do not satisfy the conditions specified above
    # #     """
    # #     invalidValues = dict()
    # #     for key in kwargs:
    # #         if not kwargs[key]:
    # #             invalidValues[key] = kwargs[key]

    # #     if invalidValues:
    # #         j.errorconditionhandler.raiseError('Invalid values: %s' %invalidValues)


