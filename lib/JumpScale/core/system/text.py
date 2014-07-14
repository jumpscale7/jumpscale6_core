CODEC='utf-8'
import time
class Text:
    @staticmethod
    def toStr(value, codec=CODEC):
        if isinstance(value, str):
            return value
        elif isinstance(value, unicode):
            return value.encode(codec)
        else:
            return str(value)

    @staticmethod
    def toAscii(value,maxlen=0):

        out=""
        for item in value:
            if ord(item)>255:
                continue
            out+=item
        if maxlen>0 and len(out)>maxlen:
            out=out[0:maxlen]            
        return out

    @staticmethod
    def toUnicode(value, codec=CODEC):
        if isinstance(value, str):
            return value.decode(codec)
        elif isinstance(value, unicode):
            return value
        else:
            return unicode(value)

    @staticmethod
    def prefix(prefix,txt):
        out=""
        txt=txt.rstrip("\n")
        for line in txt.split("\n"):
            out+="%s%s\n"%(prefix,line)
        return out

    @staticmethod
    def prefix_remove(prefix,txt,onlyPrefix=False):
        """
        @param onlyPrefix if True means only when prefix found will be returned, rest discarded
        """
        out=""
        txt=txt.rstrip("\n")
        l=len(prefix)
        for line in txt.split("\n"):
            if line.find(prefix)==0:
                out+="%s\n"%(line[l:])
            elif onlyPrefix==False:
                out+="%s\n"%(line)
        return out

    @staticmethod
    def prefix_remove_withtrailing(prefix,txt,onlyPrefix=False):
        """
        there can be chars for prefix (e.g. '< :*: aline'  and this function looking for :*: would still work and ignore '< ')
        @param onlyPrefix if True means only when prefix found will be returned, rest discarded
        """
        out=""
        txt=txt.rstrip("\n")
        l=len(prefix)
        for line in txt.split("\n"):
            if line.find(prefix)>-1:
                out+="%s\n"%(line.split(prefix,1)[1])
            elif onlyPrefix==False:
                out+="%s\n"%(line)        
        return out

    @staticmethod
    def addCmd(out,entity,cmd):
        out+="!%s.%s\n"%(entity,cmd)
        return out

    @staticmethod
    def addTimeHR(line,epoch,start=50):
        if int(epoch)==0:
            return line
        while len(line)<start:
            line+=" "
        line+="# "+time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(int(epoch)))
        return line

    @staticmethod
    def addVal(out,name,val,addtimehr=False):            
        if isinstance( val, int ):
            val=str(val)
        while len(val)>0 and val[-1]=="\n":
            val=val[:-1]
        if len(val.split("\n"))>1:
            out+="%s=...\n"%(name)
            for item in val.split("\n"):
                out+="%s\n"%(item)
            out+="...\n"
        else:
            line="%s=%s"%(name,val)
            if addtimehr:
                line=Text.addTimeHR(line,val)
            out+="%s\n"%line
        return out
