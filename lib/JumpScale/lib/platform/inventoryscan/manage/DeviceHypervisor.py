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

from JumpScale import j
from JumpScale.core.baseclasses.CMDBSubObject import CMDBSubObject


class DeviceHypervisor(CMDBSubObject):

    """
    Hypervisor info if device has a Hypervisor installed
    """
    j.cloud.cmdtools.inventoryScan
    type = j.basetype.enumeration(j.enumerators.HypervisorsType, doc='type of hypervisor', allow_none=True, flag_dirty=True)
    #, default = j.enumerators.HypervisorsType.XEN)
    vmSatistics = j.basetype.dictionary(
        doc='vmName with CPU Load percentage, memory Usage percentage', flag_dirty=True, allow_none=False, default=dict())
    timeStamp = j.basetype.string(doc='time of data collection', flag_dirty=True, allow_none=False, default='')
    vmNicSatistics = j.basetype.dictionary(doc='vmName Nics statistics', flag_dirty=True, allow_none=True, default=dict())

    def __init__(self):
        CMDBSubObject.__init__(self)
        self.type = j.enumerators.HypervisorsType.NOHYPERVISOR

    def __repr__(self):
        return str({'type': self.type, 'vmSatistics': self.vmSatistics, 'timeStamp': self.timeStamp, 'nicStatistics': self.vmNicSatistics})