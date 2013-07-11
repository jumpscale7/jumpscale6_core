
from OpenWizzy import o

try:
    import cjson as json
except:
    import json
    json.decode=json.loads
    json.encode=json.dumps
    

class JsonTool:
    def decode(self,string):
        """
        decode string to python object
        """
        string=string.replace("\\/","/")
        return json.decode(string)
        
    def encode(self,obj,pretty=False):
        """
        encode python (simple) objects to json
        """
        if pretty:
            import simplejson
            return simplejson.dumps(obj,sort_keys=True, indent=4)
        else:
            return json.encode(obj)
        
