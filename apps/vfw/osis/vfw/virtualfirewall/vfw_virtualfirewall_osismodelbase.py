from JumpScale import j

class vfw_virtualfirewall_osismodelbase(j.code.classGetJSRootModelBase()):
    def __init__(self):
        self._P_id=0
    
        self._P_gid=0
    
        self._P_nid=0
    
        self._P_name=""
    
        self._P_descr=""
    
        self._P_type=""
    
        self._P_domain=""
    
        self._P_host=""
    
        self._P_username=""
    
        self._P_password=""
    
        self._P_tcpForwardRules=list()
    
        self._P_masquerade=True
    
        self._P_wsForwardRules=list()
    
        self._P_guid=""
    
        self._P__meta=list()
    
        self._P__meta=["osismodel","vfw","virtualfirewall",1] #@todo version not implemented now, just already foreseen
    

        pass

    @property
    def id(self):
        return self._P_id
    @id.setter
    def id(self, value):
        
        if not isinstance(value, int) and value is not None:
            if isinstance(value, basestring) and j.basetype.integer.checkString(value):
                value = j.basetype.integer.fromString(value)
            else:
                msg="property id input error, needs to be int, specfile: /opt/jumpscale/apps/osis/logic/vfw/model.spec, name model: virtualfirewall, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_id=value
    @id.deleter
    def id(self):
        del self._P_id


    @property
    def gid(self):
        return self._P_gid
    @gid.setter
    def gid(self, value):
        
        if not isinstance(value, int) and value is not None:
            if isinstance(value, basestring) and j.basetype.integer.checkString(value):
                value = j.basetype.integer.fromString(value)
            else:
                msg="property gid input error, needs to be int, specfile: /opt/jumpscale/apps/osis/logic/vfw/model.spec, name model: virtualfirewall, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_gid=value
    @gid.deleter
    def gid(self):
        del self._P_gid


    @property
    def nid(self):
        return self._P_nid
    @nid.setter
    def nid(self, value):
        
        if not isinstance(value, int) and value is not None:
            if isinstance(value, basestring) and j.basetype.integer.checkString(value):
                value = j.basetype.integer.fromString(value)
            else:
                msg="property nid input error, needs to be int, specfile: /opt/jumpscale/apps/osis/logic/vfw/model.spec, name model: virtualfirewall, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_nid=value
    @nid.deleter
    def nid(self):
        del self._P_nid


    @property
    def name(self):
        return self._P_name
    @name.setter
    def name(self, value):
        
        if not isinstance(value, str) and value is not None:
            if isinstance(value, basestring) and j.basetype.string.checkString(value):
                value = j.basetype.string.fromString(value)
            else:
                msg="property name input error, needs to be str, specfile: /opt/jumpscale/apps/osis/logic/vfw/model.spec, name model: virtualfirewall, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_name=value
    @name.deleter
    def name(self):
        del self._P_name


    @property
    def descr(self):
        return self._P_descr
    @descr.setter
    def descr(self, value):
        
        if not isinstance(value, str) and value is not None:
            if isinstance(value, basestring) and j.basetype.string.checkString(value):
                value = j.basetype.string.fromString(value)
            else:
                msg="property descr input error, needs to be str, specfile: /opt/jumpscale/apps/osis/logic/vfw/model.spec, name model: virtualfirewall, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_descr=value
    @descr.deleter
    def descr(self):
        del self._P_descr


    @property
    def type(self):
        return self._P_type
    @type.setter
    def type(self, value):
        
        if not isinstance(value, str) and value is not None:
            if isinstance(value, basestring) and j.basetype.string.checkString(value):
                value = j.basetype.string.fromString(value)
            else:
                msg="property type input error, needs to be str, specfile: /opt/jumpscale/apps/osis/logic/vfw/model.spec, name model: virtualfirewall, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_type=value
    @type.deleter
    def type(self):
        del self._P_type


    @property
    def domain(self):
        return self._P_domain
    @domain.setter
    def domain(self, value):
        
        if not isinstance(value, str) and value is not None:
            if isinstance(value, basestring) and j.basetype.string.checkString(value):
                value = j.basetype.string.fromString(value)
            else:
                msg="property domain input error, needs to be str, specfile: /opt/jumpscale/apps/osis/logic/vfw/model.spec, name model: virtualfirewall, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_domain=value
    @domain.deleter
    def domain(self):
        del self._P_domain


    @property
    def host(self):
        return self._P_host
    @host.setter
    def host(self, value):
        
        if not isinstance(value, str) and value is not None:
            if isinstance(value, basestring) and j.basetype.string.checkString(value):
                value = j.basetype.string.fromString(value)
            else:
                msg="property host input error, needs to be str, specfile: /opt/jumpscale/apps/osis/logic/vfw/model.spec, name model: virtualfirewall, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_host=value
    @host.deleter
    def host(self):
        del self._P_host


    @property
    def username(self):
        return self._P_username
    @username.setter
    def username(self, value):
        
        if not isinstance(value, str) and value is not None:
            if isinstance(value, basestring) and j.basetype.string.checkString(value):
                value = j.basetype.string.fromString(value)
            else:
                msg="property username input error, needs to be str, specfile: /opt/jumpscale/apps/osis/logic/vfw/model.spec, name model: virtualfirewall, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_username=value
    @username.deleter
    def username(self):
        del self._P_username


    @property
    def password(self):
        return self._P_password
    @password.setter
    def password(self, value):
        
        if not isinstance(value, str) and value is not None:
            if isinstance(value, basestring) and j.basetype.string.checkString(value):
                value = j.basetype.string.fromString(value)
            else:
                msg="property password input error, needs to be str, specfile: /opt/jumpscale/apps/osis/logic/vfw/model.spec, name model: virtualfirewall, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_password=value
    @password.deleter
    def password(self):
        del self._P_password


    @property
    def tcpForwardRules(self):
        return self._P_tcpForwardRules
    @tcpForwardRules.setter
    def tcpForwardRules(self, value):
        
        if not isinstance(value, list) and value is not None:
            if isinstance(value, basestring) and j.basetype.list.checkString(value):
                value = j.basetype.list.fromString(value)
            else:
                msg="property tcpForwardRules input error, needs to be list, specfile: /opt/jumpscale/apps/osis/logic/vfw/model.spec, name model: virtualfirewall, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_tcpForwardRules=value
    @tcpForwardRules.deleter
    def tcpForwardRules(self):
        del self._P_tcpForwardRules


    @property
    def masquerade(self):
        return self._P_masquerade
    @masquerade.setter
    def masquerade(self, value):
        
        if not isinstance(value, bool) and value is not None:
            if isinstance(value, basestring) and j.basetype.boolean.checkString(value):
                value = j.basetype.boolean.fromString(value)
            else:
                msg="property masquerade input error, needs to be bool, specfile: /opt/jumpscale/apps/osis/logic/vfw/model.spec, name model: virtualfirewall, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_masquerade=value
    @masquerade.deleter
    def masquerade(self):
        del self._P_masquerade


    @property
    def wsForwardRules(self):
        return self._P_wsForwardRules
    @wsForwardRules.setter
    def wsForwardRules(self, value):
        
        if not isinstance(value, list) and value is not None:
            if isinstance(value, basestring) and j.basetype.list.checkString(value):
                value = j.basetype.list.fromString(value)
            else:
                msg="property wsForwardRules input error, needs to be list, specfile: /opt/jumpscale/apps/osis/logic/vfw/model.spec, name model: virtualfirewall, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_wsForwardRules=value
    @wsForwardRules.deleter
    def wsForwardRules(self):
        del self._P_wsForwardRules


    @property
    def guid(self):
        return self._P_guid
    @guid.setter
    def guid(self, value):
        
        if not isinstance(value, str) and value is not None:
            if isinstance(value, basestring) and j.basetype.string.checkString(value):
                value = j.basetype.string.fromString(value)
            else:
                msg="property guid input error, needs to be str, specfile: /opt/jumpscale/apps/osis/logic/vfw/model.spec, name model: virtualfirewall, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_guid=value
    @guid.deleter
    def guid(self):
        del self._P_guid


    @property
    def _meta(self):
        return self._P__meta
    @_meta.setter
    def _meta(self, value):
        
        if not isinstance(value, list) and value is not None:
            if isinstance(value, basestring) and j.basetype.list.checkString(value):
                value = j.basetype.list.fromString(value)
            else:
                msg="property _meta input error, needs to be list, specfile: /opt/jumpscale/apps/osis/logic/vfw/model.spec, name model: virtualfirewall, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P__meta=value
    @_meta.deleter
    def _meta(self):
        del self._P__meta


    def new_tcpForwardRule(self,value=None):

        if value==None:
            value2=j.core.codegenerator.getClassJSModel("osismodel","vfw","tcpforwardrule")()
        else:
            value2=value
        
        self._P_tcpForwardRules.append(value2)
        if self._P_tcpForwardRules[-1].__dict__.has_key("_P_id"):
            self._P_tcpForwardRules[-1].id=len(self._P_tcpForwardRules)
        return self._P_tcpForwardRules[-1]
        
    

    def new_wsForwardRule(self,value=None):

        if value==None:
            value2=j.core.codegenerator.getClassJSModel("osismodel","vfw","wsforwardrule")()
        else:
            value2=value
        
        self._P_wsForwardRules.append(value2)
        if self._P_wsForwardRules[-1].__dict__.has_key("_P_id"):
            self._P_wsForwardRules[-1].id=len(self._P_wsForwardRules)
        return self._P_wsForwardRules[-1]
        
    
