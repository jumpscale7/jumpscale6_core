from OpenWizzy import o

class Dummy(object):
    pass

class Loader(object):
    def makeAvailable(self, obj, path):
        """
        Make sure a path under a object is available
        """
        ob = obj
        for part in path.split('.'):
            if not hasattr(ob, part):
                setattr(ob, part, Dummy())
            ob = getattr(ob, part)



o.base.loader = Loader()
