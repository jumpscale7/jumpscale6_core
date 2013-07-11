
from OpenWizzy import o
import json 

gErrorConditionTypePool = dict ()
 
class ErrorConditionTypeDefinition:
    def __init__(self):
        self.setDefaults()
        
    def setDefaults(self) :
        self.categorization = "evt_category"
        self.description = "my_lovely_description"
        self.solution = "fix it!"
        self.priorityoverrule = "warning"
        self.dedupeperiod = 20
        self.active = True
        self.forwardtonoc = True
        self.storeindrp = True
        self.removetracing = True
        self.removelogging = False
    
def encodeErrorConditionTypeDefinition ( definition) :
    return definition.__dict__
        
class ErrorConditionTypeFactory :
    
    @staticmethod
    def getType( type ):
        
        if not gErrorConditionTypePool.has_key( type ) or gErrorConditionTypePool[ type ] is None:
            try :
                gErrorConditionTypePool [ type ] = ErrorConditionType( type )
            except:
                gErrorConditionTypePool [ type ] = None
                
        return gErrorConditionTypePool [ type ]
      
      
class ErrorConditionType :
    
    def __init__ (self, type):
        
        self.type = type
        self.definition = None
        self._paramDict = dict()
        
        self.loadDefinition( )
        
        
    def _buildEscalationParamDict(self):
        
        # The params dictionary should contain values for the following keys
        # - categorization
        # - description
        # - solution
        # - priorityOverrule
        # - forwardToNOC
        # - storeInDRP
        # - active
        # - clearTracing
        # - clearLogging
        # - dedupePeriod
        
        params = dict ()
        paramsmap = {'forwardtonoc': 'forwardToNOC', 'storeindrp': 'storeInDRP', 'removetracing': 'clearTracing', 
                     'priorityoverrule': 'priorityOverrule', 'removelogging': 'clearLogging', 'dedupeperiod': 'dedupePeriod'}
        for key in dir(self.definition):
            if key in ['__doc__', '__init__', '__module__', 'component_id.id', 'setDefaults']:
                continue
            if key == 'priorityoverrule':
                params[paramsmap[key]] = int(getattr(self.definition, key))
            else:
                paramvalue = paramsmap.get(key, key)
                params[paramvalue] = getattr(self.definition, key)
        return params
    
    def getEscalationParamDict(self):
        if len ( self._paramDict ) == 0 :
            self._paramDict = self._buildEscalationParamDict()    
        return self._paramDict
    
    def _getDefinitionDirectory(self) :
        return o.system.fs.joinPaths( o.dirs.cfgDir, 'evt_type_def' )
    
    def loadDefinition (self):   
        
        fileName =  self.type
        definitionFileName =  o.system.fs.joinPaths( self._getDefinitionDirectory(),  fileName )
        
        try :
            fileContents = o.system.fs.fileGetContents( definitionFileName )
            self.definition = ErrorConditionTypeDefinition() 
            self.definition.__dict__ = json.loads( fileContents )
        except Exception, ex:
            # Be sure to be backwards-compatible with eventhandler calls that do not provide event type ids
            # Raising the exception here will make the ErrorConditionTypeFactory will return None
            if len( self.type ) == 0 :
                raise
            o.logger.log( "Could not load error condition type definition for type '%s'" % str(self.type), 2  )
            o.logger.log( "%s: %s" % (ex.__class__.__name__ , ex), 6 )
            raise
            

        
