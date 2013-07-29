
from OpenWizzy import o

class FileManager():
    def __init__(self):
        self.inited=False
        
    def pathNormalizeDir(self,path):
        path=path.strip().replace("\\","/")
        if path[-1]<>"/":
            path+="/"
        return path

    def pathNormalizeFile(self,path):
        path=path.strip().replace("\\","/")
        if path[-1]=="/":
            raise RuntimeError("File %s cannot end on /"%path)
        return path

    def _ignorePath(self,item):
        #items=[]
        #for item in os.listdir(path):
        ext=o.system.fs.getFileExtension(item)
        if item.find(".quarantine")==0 or item.find(".tmb")==0:
            try:
                o.system.fs.remove(item)
            except:
                pass
            return True
        elif ext=="pyc":
            return True
        #else:
            #items.append(item)
