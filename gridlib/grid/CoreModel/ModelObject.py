import struct


class ModelObject():
    def __init__(self, ddict={}):
        self.__dict__=ddict


    def getCategory(self):
        return self.category

    def getUniqueKey(self):
        """
        return unique key for object, is used to define unique id
        """
        return self.guid

    def getContentKey(self):
        """
        """
        return self.guid

    def getSetGuid(self):
        """
        use osis to define & set unique guid (sometimes also id)
        """
        if self.guid:
            return self.guid
        else:
            return None

    def getIDs(self):
        if self.guid:
            return struct.unpack("<HHH",self.guid)
        else:
            return None

    def getObjectType(self):
        return 13

    def getVersion(self):
        return 1

    def getMessage(self):
        #[$objecttype,$objectversion,guid,$object=data]
        return [13,1,self.guid,self.__dict__]

    def getSerializable(self):
        return self.__dict__.copy()

