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

    def getGitClient(self,repoName="",branch=None):
        """
        """
        #if self.gitclients.has_key(repoName):
            #return self.gitclients[repoName]
        #@todo P2 cache the connections but also use branchnames

        if repoName=="":
            repoName=self.findRepoFromGitlab(repoName)
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
        j.clients.gitlab.log("init git client ##%s## on path:%s"%(repoName,self.getRepoPathLocal(repoName)),category="getclient")
        cl = j.clients.git.getClient(self.getCodeFolder(repoName), url, branchname=branch)
        # j.clients.gitlab.log("git client inited for repo:%s"%repoName,category="getclient")
        self.gitclients[repoName]=cl
        return cl

    def getCodeFolder(self, repoName):
        return "%s/%s/%s/" % (j.dirs.codeDir,"git_%s"%self.accountName,repoName)

