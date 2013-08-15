from HgLibClient import HgLibClient

class HgLibFactory:
    def getClient(self, hgbasedir, remoteUrl="", branchname="", cleandir=False):
        """
        return a mercurial tool which you can help to manipulate a hg repository
        @param base dir where local hgrepository will be stored
        @branchname "" means is the tip, None means will try to fetch the branchname from the basedir
        @param remote url of hg repository, e.g. https://login:passwd@bitbucket.org/despiegk/ssospecs/  #DO NOT FORGET LOGIN PASSWD
        """
        if not isinstance(cleandir, bool):
            raise ValueError("cleandir needs to be boolean")
        return HgLibClient(hgbasedir, remoteUrl, branchname=branchname, cleandir=cleandir)
