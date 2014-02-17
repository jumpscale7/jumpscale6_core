import json
from JumpScale import j
from JumpScale.core.baseclasses import BaseEnumeration

from GitlabConfigManagement import *
# import urllib
# import requests
# from requests.auth import HTTPBasicAuth
import gitlab
import os

from GitlabInstance import *

# INFOCACHE = dict()

class GitlabFactory:
    """
    Gitlab client enables administrators and developers leveraging Gitlab services through JumpScale
    """

    def __init__(self):
        self.config=GitlabConfigManagement()
        self.connections={}
        j.logger.consolelogCategories.append("gitlab")

    def get(self,account):
        config=self._accountGetConfig(account)
        return GitlabInstance(config["addr"], config["login"], config["passwd"], config["token"])

    def log(self,msg,category="",level=5):
        category="gitlab.%s"%category
        category=category.rstrip(".")
        j.logger.log(msg,category=category,level=level)

    def accountAdd(self,account="",addr="",login="",passwd=""):
        """
        All params need to be filled in, when 1 not filled in will ask all of them
        """
        if account<>"" and login<>"" and passwd<>"":
            try:
                self.config.remove(account)
            except:
                pass
            self.config.add(account, {"addr":addr,"login": login, "passwd": passwd})
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
            j.console.echo("Did not find account name %s for gitlab, will ask for information for this account" % accountName)
            self.config.add(accountName)

        return self.config.getConfig(accountName)

    def getGitlabClient(self, accountName, repoName, branch='default'):
        url, accountLogin, accountPasswd = self._getRepoInfo(accountName, repoName, branch)
        if self.connections.has_key(repoName):
            return self.connections[repoName]
        self.connections[repoName] = GitlabInstance(accountName,url,login=accountLogin,passwd=accountPasswd)
        return self.connections[repoName]

    def getRepoInfo(self, accountName, repoName):
        from IPython import embed
        print "DEBUG NOW ooo"
        embed()
        
        url = "https://gitlab.org/api/1.0/repositories/%s/%s" % (accountName, repoName)
        result = INFOCACHE.get(url)
        if result:
            return result
        result = requests.get(url)
        if result.ok:
            INFOCACHE[url] = result.json()
        else:
            INFOCACHE[url] = result.status_code
        return INFOCACHE[url]

    def _getRepoInfo(self, accountName, repoName, branch="default"):
        loginInfo = ''
        login = None
        passwd = None
        repoInfo = self.getRepoInfo(accountName, repoName)

        config = self._accountGetConfig(accountName)
        login = config["login"]
        passwd = config["passwd"]

        if login.find("@login")<>-1:
            if j.application.shellconfig.interactive:
                login=j.gui.dialog.askString("  \nLogin for gitlab account %s" % accountName)
            else:
                login = ""
            self.config.configure(accountName,{'login': login})
        
        if passwd.find("@passwd")<>-1:
            if j.application.shellconfig.interactive:
                passwd = j.gui.dialog.askPassword("  \nPassword for gitlab account %s" % accountName, confirm=False)
            else:
                passwd = ""
            self.config.configure(accountName,{'passwd': passwd})
        if login:
            loginInfo = '%s:%s@' % (login, passwd)

        if repoInfo == 404: #not found
            j.errorconditionhandler.raiseOperationalCritical("Repo %s/%s is invalid" % (accountName, repoName))
        # elif repoInfo == 403: #forbidden
        
        if login not in ('hg', 'ssh'):
            url = " https://%sgitlab.org/%s/" % (loginInfo, accountName)
        else:
            url=" ssh://hg@gitlab.org/%s/" % (accountName)
        # if login==None or login.strip()=="":
        #     raise RuntimeError("Login cannot be empty, url:%s"%url)

        return url, login, passwd

    # def getMecurialRepoClient(self, accountName, reponame,branch="default"):
    #     gitlab_connection = self.getGitlabRepoClient(accountName, reponame)
    #     return gitlab_connection.getMercurialClient(reponame,branch=branch)

