from OpenWizzy import o
class mainclass(o.core.osis.getOsisImplementationParentClass("_modelobjects")):
    """
    Defeault object implementation
    """

    def _getDB(self):
        return q.db.keyvaluestore.getArakoonStore('osis')
