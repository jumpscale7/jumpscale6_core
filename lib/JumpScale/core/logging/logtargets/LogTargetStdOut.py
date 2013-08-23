
class LogTargetStdOut(object):
    
    def __init__(self):
        """
        """
        self.enabled = False
        self.screenwidth=120
        self.name="stdout"
        
    def checkTarget(self):
        """
        check status of target, if ok return True
        for std out always True
        """
        True
    
    def log(self, log):
        """
        log to stdout use q.loghandler.reformatMessageToHR() 
        example 1|754545|performancetester|5||copy file from a to b
        @param message string in format time(epoch)|source(string)|level(0-10)|tags|logmessage\n 
        """    
        print(log)

        # logobj=j.logger.getLogObject(message)
        # message = str(logobj)#will render differently for logs and events
        # formattedOut = screenline = message[:self.screenwidth]
        # message = message[self._screenWidth:]
        # tabLength = len(pprint.pformat('\t'))
        # tabLength = tabLength if tabLength < self._screenWidth else 0
        # indent = ' ' * tabLength
        # extraLinesLength = self.screenWidth - tabLength
        # while screenline:
        #     screenline = message[:extraLinesLength]
        #     message = message[extraLinesLength:]
        #     formattedOut = '%s\n%s%s'%(formattedOut, indent, screenline)

        # print formattedOut
        # return True
        
    def __eq__(self, other):
        if not other:
            return False
        if not isinstance(other, LogTargetStdOut):
            return False
        
        return True
    
    def close(self):
        pass
