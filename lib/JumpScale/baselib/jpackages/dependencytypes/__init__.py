class AbstractPackage(object):
    def __init__(self, name, minversion='', maxversion=''):
        self.name = name
        self.minversion = minversion
        self.maxversion = maxversion

    def pm_getDependencies(self, *args, **kwargs):
        return list()

    def __str__(self):
        return "%s: %s %s %s" % (self.__class__.__name__, self.name, self.minversion, self.maxversion)
