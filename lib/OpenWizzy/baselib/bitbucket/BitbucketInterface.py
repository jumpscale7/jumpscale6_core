from OpenWizzy import o

class RepoList():
    pass

class Account():
    def __init__(self):
        self.items=RepoList()
        
    def getRepo(self,reponame=""):
        if reponame=="":
            reponames= self.mercurialClients.keys()
            reponame=o.console.askChoice(reponames,"Choose Repo",True)     
        if self.mercurialClients.has_key(reponame):
            return self.mercurialClients[reponame]
        else:
            raise RuntimeError("Could not find repo with name %s from account %s" % (reponame,self.name))

    def _repoSelect(self,reponames=[],allRepos=False):
        if allRepos:
            reponames= self.mercurialClients.keys()
        if reponames==[]:
            reponamesAll= self.mercurialClients.keys()
            reponames=o.console.askChoiceMultiple(reponamesAll,"Choose Repos",True)     
        return reponames

        
    def push(self,reponames=[],message="",commit=True,addremove=True,checkIgnore=True,pull=None,all=False):
        """
        @param checkIgnore, will check the ignore list in the account (on /code/$accountname/.ignore...)
        @commit before pushing will commit
        @addremove before pushing will addremove            
        @param all, if all will try to push all repo's of this account
        """
        reponames=self._repoSelect(reponames,allRepos=all) 
        if pull==None:
            pull=o.console.askYesNo("Do you want to pull first?")
        for reponame in reponames:
            self._push(reponame,message=message,commit=commit,addremove=addremove,checkIgnore=checkIgnore,pull=pull)

    def pull(self,reponames=[],message="",update=True,merge=True,checkIgnore=True,all=False,force=False):
        """
        @param checkIgnore, will check the ignore list in the account (on /code/$accountname/.ignore...)
        @param all, if all will try to push all repo's of this account
        """
        reponames=self._repoSelect(reponames,allRepos=all) 
        for reponame in reponames:
            self._pull(reponame,message=message,update=update,merge=merge,checkIgnore=checkIgnore,force=force)

    def pullForceUpdate(self,reponames=[],checkIgnore=True,all=False):
        """
        @param checkIgnore, will check the ignore list in the account (on /code/$accountname/.ignore...)
        @param all, if all will try to push all repo's of this account
        """
        reponames=self._repoSelect(reponames,allRepos=all) 
        for reponame in reponames:
            self._pull(reponame,message="",update=True,merge=False,checkIgnore=checkIgnore,force=True)


    def status(self,reponames=[],checkIgnore=True,all=False):
        """
        @param checkIgnore, will check the ignore list in the account (on /code/$accountname/.ignore...)
        @param all, if all will try to push all repo's of this account
        """        
        reponames=self._repoSelect(reponames,allRepos=all) 
        for reponame in reponames:
            self._status(reponame,checkIgnore=checkIgnore)

#@todo P1 :thomas write decent descriptions in doc sections

class BitbucketInterface():
    """
    interface on i
    """
    
    def __init__(self):
        try:
            self.init()
        except:
            o.console.echo("Cannot dynamically load the bitbucket instances, please call i.bitbucket.init()\n")
            
    def getRepo(self,accountname="",reponame=""):
        account=self.getAccount(accountname)
        return account.getRepo(reponame)
        
    def getAccount(self,accountname=""):
        if accountname=="":
            accounts= o.clients.bitbucket.config.list()
            if len(accounts)==1:
                accountname=accounts[0]
            else:
                accountname=o.console.askChoice(o.clients.bitbucket.config.list(),"Choose Bitbucket Account",True)
        if not self.__dict__.has_key(accountname):
            return self._populate1account(accountname)
        else:
            return  self.__dict__[accountname]
        
    def _populate1account(self,account):
        bbc=o.clients.bitbucket.getBitbucketConnection(account)
        self.__dict__[account]=Account()
        self.__dict__[account].name=account
        names=bbc.getRepoNamesLocal()
        self.__dict__[account]._pull=bbc.pull
        self.__dict__[account]._push=bbc.push
        self.__dict__[account]._status=bbc.status  
        self.__dict__[account].mercurialClients={}
        for name in names:
            self.__dict__[account].items.__dict__[name]=bbc.getMercurialClient(name)                
        self.__dict__[account].mercurialClients=self.__dict__[account].items.__dict__
        return  self.__dict__[account]
        
    def init(self):
        accounts=o.clients.bitbucket.config.list()
        for account in accounts:
            self._populate1account(account)
                
            
            
            
        
