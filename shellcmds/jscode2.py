#!/usr/bin/env jspython
from JumpScale import j

from JumpScale.baselib import cmdutils
import JumpScale.baselib.git

import sys,time

j.application.start("jscode2")

if j.application.sandbox:
    raise RuntimeError("Cannot use jscode in sandboxed mode, is not supported, install in development mode.")

parser = cmdutils.ArgumentParser()
parser.add_argument("action", choices=['commit','push','update','status'], help='Command to perform')

parser.add_argument('-m','--message',help='commit message')
parser.add_argument('-b','--branch',help='branch')

parser.add_argument('-a','--accounts',help='comma separated list of accounts, * is all')
parser.add_argument('-r','--repos',help='comma separated list of repos, will look for the accounts')

parser.add_argument('-u','--update',required=False, action='store_true',help='update merge before doing push or commit')

parser.add_argument('-f','--force',required=False, action='store_true',help='auto answer yes on every question')
parser.add_argument('-d','--deletechanges',required=False, action='store_true',help='will delete all changes when doing update')


# parser.add_argument('-m','--message',required=False, action='store_true',help='commit message')

opts = parser.parse_args()

if opts.accounts==None and opts.repos==None:
    if j.system.fs.exists("%s/%s"%(j.system.fs.getcwd(),".git")):
        #we are in repo
        opts.repos=j.system.fs.getBaseName(j.system.fs.getcwd())
        opts.accounts=j.system.fs.getBaseName(j.system.fs.getParent(j.system.fs.getcwd()))


if opts.branch<>None and opts.action in ['status']: 
    raise RuntimeError("Cannot specify branch when asking status")

def getRepos():
    result=[]

    if opts.accounts=="*":
        accounts=j.system.fs.listDirsInDir("/opt/code/github", recursive=False, dirNameOnly=True, findDirectorySymlinks=True)
    elif opts.accounts<>None:
        accounts=[item.strip() for item in opts.accounts.split(",")]
    else:
        accounts=j.system.fs.listDirsInDir("/opt/code/github", recursive=False, dirNameOnly=True, findDirectorySymlinks=True)
                        
        accounts=j.console.askChoiceMultiple(accounts,"select github accounts")

    for account in accounts:
        accountdir="/opt/code/github/%s"%account
        if j.system.fs.exists(accountdir):
            if opts.repos==None:
                reponames=j.system.fs.listDirsInDir(accountdir,recursive=False, dirNameOnly=True, findDirectorySymlinks=True)
                if  not opts.action in ['status']:                    
                    reponames=j.console.askChoiceMultiple(reponames,"select repos")
            elif opts.repos=="*":
                reponames=j.system.fs.listDirsInDir(accountdir,recursive=False, dirNameOnly=True, findDirectorySymlinks=True)
            else:
                reponames=[item.strip() for item in opts.repos.split(",")]

            for reponame in reponames:

                if reponame.find("__")<>-1:
                    branch,reponame=reponame.split("__",1)
                    repodir="%s/%s__%s"%(accountdir,branch,reponame)
                else:
                    branch="master"
                    repodir="%s/%s"%(accountdir,reponame)
                    #@todo need to add back
                    # raise RuntimeError("branch not specified in reponame.")

                if not j.system.fs.exists(path=repodir):
                    raise RuntimeError("Could not find mercurial repo on %s"%repodir)

                cl=j.clients.git.getClient(repodir)
                result.append((account,reponame,branch,cl,repodir))
    return result

repos=getRepos()

if opts.action == "status":
    print "\n\nSTATUS: account reponame                  branch added:modified:deleted   insyncwithremote?   localrev       remoterev"
    print "========================================================================================================================="


for account,reponame,branch,client,path in repos:

    if opts.action == "update" and opts.deletechanges:
        print "force update %s/%s"%(account,reponame)
        client.pull()
        client.update(force=True)
        continue

    if opts.action in ['status','commit','push','update']:

        mods=client.getModifiedFiles()

        # lrev,lid,ttype,branch,user,msg,ddate=client.client.tip()
        branch=client.branchName

        if opts.branch<>None:
            if branch<>opts.branch:
                print "set branch:%s"%opts.branch
                from IPython import embed
                print "DEBUG NOW not suported yet"
                embed()
                
                cmd="cd %s;hg branch %s"%(path,opts.branch)
                j.system.process.execute(cmd,dieOnNonZeroExitCode=False, outputToStdout=True, useShell=True, ignoreErrorOutput=False)                
                cmd="cd %s;hg update %s"%(path,opts.branch)
                j.system.process.execute(cmd)
                print "updated to branch:%s"%opts.branch
                lrev,lid,ttype,branch,user,msg,ddate=client.client.tip()
                branch=client.getbranchname()


        # changesets=bitbucket.getChangeSets(reponame=reponame,limit=1)
        # if changesets.has_key("error"):
        #     print "could not process repo: %s %s error:%s"%(account,reponame,changesets["error"]["message"])
        #     # print changesets            
        #     continue
        # try:
        #     remotelastrevision=changesets["changesets"][0]["revision"]
        # except Exception,e:
        #     from IPython import embed
        #     print "DEBUG NOW jscode check error from changeset pull"
        #     embed()
            
        # rid=changesets["changesets"][0]["raw_node"] #remoteid

        # if lid==rid:
        #     reposync="Y"
        # else:
        #     reposync="N"

        reposync="?"
        lrev="?"
        remotelastrevision="?"

        nrmods= len(mods["D"])+len(mods["M"])+len(mods["N"])+len(mods["R"])

        if nrmods>0:
            reposync="N"            


        print "%-15s %-25s %-10s n%-3s:m%-3s:d%-3s:r%-6s reposync:%-9s  lrev:%-9s rrev:%-5s" %(account,reponame,client.branchName,\
            len(mods["N"]),len(mods["M"]),len(mods["D"]),len(mods["R"]),\
            reposync,\
            lrev,remotelastrevision)

    if opts.action in ['commit']:
        if nrmods==0:
            print "no need to commit is in sync"
            continue

    # if opts.action in ['update']:
    #     if nrmods==0 and reposync=="Y":
    #         print "no need to update, repo is in sync"
    #         continue

    if opts.action in ['commit']:        
        if nrmods==0:
            print "no need to commit, no mods"
            continue

    if nrmods>0:
        print "MODS:"
        for key,item in mods.iteritems():
            if len(item)>0:
                print " %s"%key
                for subitem in item:
                    print "    - %s"%(subitem)


    if opts.action in ['commit','push','update']:
        if opts.message==None and nrmods>0:
            opts.message=j.console.askString("commit message")    
        if nrmods>0:
            print "ADD/REMOVE/COMMIT"
            client.commit(message=opts.message, addremove=True)

    if opts.update or opts.action =='update' or opts.action =='push':
        print "PULL"
        client.pull()
    
    if opts.action =='push':        
        print "PUSH"
        client.push()


j.application.stop()