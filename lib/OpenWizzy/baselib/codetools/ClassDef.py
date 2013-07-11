# <License type="Sun Cloud BSD" version="2.2">
#
# Copyright (c) 2005-2009, Sun Microsystems, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# 3. Neither the name Sun Microsystems, Inc. nor the names of other
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY SUN MICROSYSTEMS, INC. "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL SUN MICROSYSTEMS, INC. OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# </License>

from OpenWizzy import o
import PropertyDef

class ClassDef:
    
    def __init__(self, filePath, name="", inheritance="", comments=""):
        self.filePath=filePath
        self.name=name
        self.comment=comments
        self.inheritanceString=inheritance.strip()
        if self.inheritanceString == "":
            self.inheritedClasses = []
        else:
            self.inheritedClasses = [c.strip() for c in inheritance.split(",")]
            
        self.docstring=""
        self.propertyDefs=[]
        self.methodDefs=[]
        self.preinitEntries = [] # Will contain a list of dicts, representing instances of the class to be pre-initialized. The dicts contain key/value pairs representing the membername/defaultvalue of the instances.
        self.code="" #content of file describing class

    def addPropertyDef(self,prop):
        self.propertyDefs.append(prop)

    def addMethodDef(self,method):
        self.methodDefs.append(method)

    def getProp(self, propname, includeInheritedClasses = False):
        """
        Returns the propertyDef of the property with the given name.
        Returns None if the property could not be found.
        """
        for propdef in self.propertyDefs:
            if propdef.name==propname:
                return propdef
        if includeInheritedClasses:
            for c in self.inheritedClasses:
                classDef = self.codeFile.codeStructure.getClass(c)
                pd = classDef.getProp(propname, True)
                if not pd == None:
                    return pd
        o.logger.log("Could not find the property [%s]" % propname, 3)
        return None