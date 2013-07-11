from BucketLoader import BucketLoader
from SpacesLoader import SpacesLoader
from ActorsLoader import ActorsLoader

class Appserver6LoaderFactory():
    def getActorsLoader(self):
        return ActorsLoader()
    def getBucketsLoader(self):
        return BucketLoader()
    def getSpacesLoader(self):
        return SpacesLoader()