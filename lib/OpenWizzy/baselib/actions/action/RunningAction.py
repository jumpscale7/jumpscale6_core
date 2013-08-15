# <License type="Qlayer BSD" version="2.0">
# 
# Copyright (c) 2005-2008, Qlayer NV.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
# 
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
# 
# * Neither the name Qlayer nor the names of other contributors
#   may be used to endorse or promote products derived from this
#   software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY QLAYER "AS IS" AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL QLAYER BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# </License>
 
class RunningAction:
    description = ""
    '''Action description

    @type: string
    '''

    resolutionMessage = ""
    '''Action resolution message

    @type: string
    '''

    errorMessage = ""
    '''Action error message

    @type: string
    '''

    show = True
    '''Display action

    @type: bool
    '''

    interrupted = False
    '''Whether the action was interrupted

    @type: bool
    '''

    output = ""
    '''Action output

    @type: string
    '''

    messageLevel = 1
    '''TODO'''
    
    def __init__(self, description, errorMessage, resolutionMessage, show=True, messageLevel=1):
        '''Initialize a new L{RunningAction}

        @param description: Action description
        @type description: string
        @param resolutionMessage: Action resolution message
        @type resolutionMessage: string
        @param show: Display action
        @type show: bool
        @param messageLevel: Message level
        @type messageLevel: number
        '''

        self.description = description
        self.resolutionMessage = resolutionMessage
        self.errorMessage = errorMessage
        self.show = show
        self.messageLevel = messageLevel