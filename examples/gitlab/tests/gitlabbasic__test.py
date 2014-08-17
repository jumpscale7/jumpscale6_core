from JumpScale import j


descr = """
basic tests of gitlab
"""

organization = "jumpscale"
author = "incubaid"
license = "bsd"
version = "1.0"
category = "gitlab.basic"
enable=True
priority=1
send2osis=False

import JumpScale.baselib.gitlab


class TEST():


    def setUp(self):
        self.gitlab=j.clients.gitlab.get("incubaid")

    def test_userExists(self):
        if not self.gitlab.existsUser("testuser"):
            raise RuntimeError("make sure there is user testuser")

    def test_groupExists(self):
        if not self.gitlab.existsGroup("test"):
            raise RuntimeError("make sure there is group test")

    def test_userInGroup(self):
        if 'test' in self.gitlab.groups2id:
            members = self.gitlab.listgroupmembers(self.gitlab.groups2id['test'])
            for member in members:
                if member['username'] == 'testuser':
                    return
            raise RuntimeError("user testuser does not belong to group test")
        else:
            raise RuntimeError("group test does not exist")

    def test_userLogin(self):
        # testuser/rooter123
        if not self.gitlab.login('testuser', 'rooter123'):
            raise RuntimeError("username/password do not match")

    def test_createDeleteProject(self):
        #create project testproj, in group test
        #check tesproj exists in namespace test (it comes from group)
        #checkout the project underneath /opt/code/git_$namespace/$name
        #put readme file inside
        #push changes to repo

        if not self.gitlab.existsProject("testuser", "testproj"):
            result = self.gitlab.createprojectuser(self.gitlab.users2id['testuser'], "testproj", public=1)

        client = self.gitlab.getGitClient("testuser", "testproj", clean=True)
        j.system.fs.writeFile(j.system.fs.joinPaths(client.gitBaseDir, 'readme.txt'), 'sample readme file')
        client.addFiles(['readme.txt'])
        client.push()

    def tearDown(self):
        pass
