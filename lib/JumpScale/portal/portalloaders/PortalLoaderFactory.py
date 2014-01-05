from JumpScale import j
from BucketLoader import BucketLoader
from SpacesLoader import SpacesLoader
from ActorsLoader import ActorsLoader


class PortalLoaderFactory():

    def getActorsLoader(self):
        return ActorsLoader()

    def getBucketsLoader(self):
        return BucketLoader()

    def getSpacesLoader(self):
        return SpacesLoader()

    def getTemplatesPath(self):
        dirname = j.system.fs.getDirName(__file__)
        return j.system.fs.joinPaths(dirname, 'templates')

    