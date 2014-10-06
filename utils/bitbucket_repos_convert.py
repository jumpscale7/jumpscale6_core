from JumpScale import j
import JumpScale.baselib.mercurial
import requests

def list_repos(account, username, password):
    uri = 'https://%s:%s@bitbucket.org/api/1.0' % (username, password)
    result = requests.get('%s/users/%s' % (uri, account)).json()
    return [r['name'] for r in result['repositories'] if r['scm'] == 'hg']

def create_repo(username, password, oldrepodata):
    uri = 'https://%s:%s@bitbucket.org/api/1.0' % (username, password)
    data = oldrepodata.copy()
    data['scm'] = 'git'
    return requests.post('%s/repositories' % uri, data=data).json()

def get_repo_info(account, username, password, name):
    uri = 'https://%s:%s@bitbucket.org/api/1.0' % (username, password)
    return requests.get('%s/repositories/%s/%s' % (uri, account, name)).json()

def rename_repo(account, username, password, oldname, newname):
    uri = 'https://%s:%s@bitbucket.org/api/1.0' % (username, password)
    result = requests.put('%s/repositories/%s/%s' % (uri, account, oldname), data={'name': newname}).json()
    return result['name'] == newname

def main():
    account_name = j.console.askString('Bitbucket account name', defaultparam='incubaid')
    username = j.console.askString('Bitbucket user name (must have access to account repos)', defaultparam='despiegk')
    password = j.console.askPassword('Bitbucket user password')
    print 'Fetching account "%s" repos...' % account_name
    selected_repos_names = j.console.askChoiceMultiple(list_repos(account_name, username, password))

    tmp_repos_dir = j.system.fs.joinPaths(j.dirs.codeDir, 'tmp')
    j.system.fs.createDir(tmp_repos_dir)

    print 'Downloading the migration tool...'
    tool_dir = j.system.fs.joinPaths(tmp_repos_dir, 'fast-export')
    j.system.fs.removeDirTree(tool_dir)
    j.system.process.execute('cd %s; git clone git@github.com:frej/fast-export.git' % tmp_repos_dir)

    print 'The script will migrate the following repo(s): %s' % ', '.join(selected_repos_names)
    for repo in selected_repos_names:
        print 'Cloning repo: %s...' % repo
        hg_repo_dir = j.system.fs.joinPaths(tmp_repos_dir, 'hg_%s' % repo)
        git_repo_dir = j.system.fs.joinPaths(tmp_repos_dir, repo)
        j.system.fs.createDir(hg_repo_dir)
        j.clients.mercurial.getClient(hg_repo_dir, 'https://%s:%s@bitbucket.org/%s/%s' % (username, password, account_name, repo))
        old_repo_data = get_repo_info(account_name, username, password, repo)
        print 'Renaming Mercurial repo "%s" on Bitbucket to "hg_%s"...' % (repo, repo)
        if not rename_repo(account_name, username, password, repo, 'hg_%s' % repo):
            print "ERROR: Couldn't rename repo '%s' to 'hg_%s'" % (repo, repo)
            print 'ABORTED repo: %s. Will process next one (if any)...' % repo
            continue
        print 'Creating Git repo "%s" on Bitbucket...' % repo
        create_repo(username, password, old_repo_data)
        print 'Converting to Git...'
        j.system.fs.createDir(git_repo_dir)
        j.system.process.execute('cd %s; git init; %s/hg-fast-export.sh -r %s' % (git_repo_dir, tool_dir, hg_repo_dir), outputToStdout=True)
        j.system.process.execute('cd %s; git remote add origin git@bitbucket.org:%s/%s.git' % (git_repo_dir, account_name, repo))
        print 'Pushing the new Git repo to Bitbucket...'
        j.system.process.execute('cd %s; git add .; git push -u origin --all; git push -u origin --tags; git checkout;' % git_repo_dir)
        print 'Completed'

    print 'Cleaning up...'
    j.system.fs.removeDirTree(tmp_repos_dir)
    print 'Finished.'

if __name__ == '__main__':
    print 'This script migrates selected Bitbucket repo(s) from Mercurial to Git, and uploads the new Git repo(s) back to Bitbucket'
    print 'This script will need admin access on selected repo(s) to rename them'
    main()