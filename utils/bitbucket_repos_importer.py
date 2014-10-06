from JumpScale import j
import JumpScale.baselib.mercurial
import requests
import boto
from boto.gs.connection import GSConnection

gs_access_key_id = j.application.config.get('gs.access_key_id')
gs_secret_access_key = j.application.config.get('gs.secret_access_key')

def repos_list(account, username, password):
    uri = 'https://%s:%s@bitbucket.org/api/1.0' % (username, password)
    result = requests.get('%s/users/%s' % (uri, account)).json()
    return [r['name'] for r in result['repositories']]

def main():
    output_path = j.console.askString('Output path (dir will be created if not there)', defaultparam=j.system.fs.joinPaths(j.dirs.codeDir, '_backup'))
    account_name = j.console.askString('Bitbucket account name', defaultparam='incubaid')
    username = j.console.askString('Bitbucket user name (must have access to account repos)', defaultparam='despiegk')
    password = j.console.askPassword('Bitbucket user password')

    if j.system.fs.exists(output_path):
        j.system.fs.removeDirTree(output_path)
    j.system.fs.createDir(output_path)
    tmp_repos_dir = j.system.fs.joinPaths(output_path, 'tmp')
    j.system.fs.createDir(tmp_repos_dir)

    repos_names = repos_list(account_name, username, password)
    print 'The script will backup %s repos' % len(repos_names)
    for repo in repos_names:
        print 'Backing up repo: %s...' % repo
        tmp_repo_dir = j.system.fs.joinPaths(tmp_repos_dir, repo)
        j.system.fs.createDir(tmp_repo_dir)
        j.clients.mercurial.getClient(tmp_repo_dir, 'https://%s:%s@bitbucket.org/%s/%s' % (username, password, account_name, repo))
        print 'Compressing...'
        j.system.fs.targzCompress(tmp_repo_dir, j.system.fs.joinPaths(output_path, 'hg_%s.tgz' % repo))
        print 'Completed'

    print 'Cleaning up...'
    j.system.fs.removeDirTree(tmp_repos_dir)
    print 'Backup completed on local file system'
    # print 'Now will upload to Google Cloud Storage...'

    # gs_connection = boto.connect_gs(gs_access_key_id, gs_secret_access_key)

if __name__ == '__main__':
    print 'This script backs all Bitbucket repos of the given account up in ZIP format to local file system'
    main()