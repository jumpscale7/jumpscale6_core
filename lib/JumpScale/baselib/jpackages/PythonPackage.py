from JumpScale import j

class PythonPackage(object):
    def install(self, name, version=None):
        # TODO validata versions
        j.system.process.execute("pip install '%s'" % name)
