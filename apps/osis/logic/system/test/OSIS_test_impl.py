from JumpScale import j
ujson = j.db.serializers.getSerializerType('j')
parentclass=j.core.osis.getOsisImplementationParentClass("system")  #is the name of the namespace

class mainclass(parentclass):
    """
    """
