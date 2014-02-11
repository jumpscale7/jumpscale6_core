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
import JumpScale.baselib.git

class GitlabInstance(Gitlab):

    def __init__(self, addr, login, passwd, token):
        self.addr=addr
        Gitlab.__init__(self, addr, token=token)
        # self.accountPathLocal = j.system.fs.joinPaths("/opt/code",accountName)
        # j.system.fs.createDir(self.accountPathLocal)
        # self._gitlab = gitlab.Gitlab(self.addr)
        self.login(login, passwd)
        # for item in dir(self._gitlab):
        #     if item[0]<>"_":
        #         setattr(self,item,getattr(self._gitlab,item))
        self.gitclients={}

    def getGitClient(self,accountName, repoName="",branch=None):
        """
        """
        #if self.gitclients.has_key(repoName):
            #return self.gitclients[repoName]
        #@todo P2 cache the connections but also use branchnames
        self.accountName = accountName
        if repoName=="":
            repoName=self.findRepoFromGitlab(repoName)
        if repoName=="":
            raise RuntimeError("reponame cannot be empty")

        url = 'http://%s' % self.addr
        if url[-1]<>"/":
            url=url+"/"

        url += "%s/%s.git" % (accountName, repoName)

        j.clients.gitlab.log("init git client ##%s## on path:%s"%(repoName,self.getCodeFolder(repoName)),category="getclient")
        cl = j.clients.git.getClient(self.getCodeFolder(repoName), url, branchname=branch)
        # j.clients.gitlab.log("git client inited for repo:%s"%repoName,category="getclient")
        self.gitclients[repoName]=cl
        return cl

    def getCodeFolder(self, repoName):
        return "%s/%s/%s/" % (j.dirs.codeDir,"git_%s"%self.accountName,repoName)

