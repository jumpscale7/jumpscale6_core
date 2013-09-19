from JumpScale import j

class PythonPackage(object):
    def install(self, name, version=None):
        if version:
        	j.system.process.execute("pip install '%s%s'" % (name, version))
        j.system.process.execute("pip install '%s'" % name)
