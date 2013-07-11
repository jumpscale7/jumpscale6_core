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

import os.path

from OpenWizzy import o
from OpenWizzy.core.extensions.PMExtensions import SYSTEM_EXTENSIONS, HOOK_POINTS
from OpenWizzy.core.inifile import IniFile

def list():
    '''List all extensions known on the system'''
    return tuple(sorted(extension['qlocation'] \
            for extension in SYSTEM_EXTENSIONS))

def _findExtension(qlocation):
    '''Finds extension info for an extension at a given qlocation

    @param qlocation: Hook location of the extension
    @type qlocation: string

    @returns: Hook information
    @rtype: dict
    '''
    correct_hook = None

    for hook in SYSTEM_EXTENSIONS:
        if hook['qlocation'] == qlocation:
            correct_hook = hook
            break

    if not correct_hook:
        raise ValueError('Unknown extension %s' % qlocation)

    return correct_hook

def _setExtensionEnabled(qlocation, value):
    '''Set the enabled value of a given extension to a given value

    @param qlocation: Hook location of the extension
    @type qlocation: string
    @param value: Value to set the 'enabled' configuration value to
    @type value: string
    '''
    hook = _findExtension(qlocation)

    extension_config = o.system.fs.joinPaths(hook['extension_path'],
                                                            'extension.cfg')
    ini = IniFile(extension_config)

    ini.setParam(hook['hookid'], 'enabled', value)

    ini.write(extension_config)


def enable(qlocation):
    '''Enable an extension

    @param qlocation: Hook location of the extension
    @type qlocation: string
    '''
    _setExtensionEnabled(qlocation, '1')

def disable(qlocation):
    '''Disable an extension

    @param qlocation: Hook location of the extension
    @type qlocation: string
    '''
    _setExtensionEnabled(qlocation, '0')

def pm_sync():
    '''Rescan extension folder and load new extensions'''
    known_hooks = set(hook['qlocation'] for hook in SYSTEM_EXTENSIONS \
                      if hook['enabled'])
    for extensionmanager in HOOK_POINTS.itervalues():
        hooks = extensionmanager.findExtensionInfo(warn_old_extensions=False)
        for hook in hooks:
            if hook['qlocation'] not in known_hooks and \
                hook['qlocation'].startswith(extensionmanager.hook_base_name):
                #New extension
                extensionmanager.populateExtension(hook['extension_path'],
                        hook)
                SYSTEM_EXTENSIONS.append(hook)

def pm_syncExtension(qlocation):
    '''Rescan extension folder and load new extension with the given qlocation'''
    known_hooks = set(hook['qlocation'] for hook in SYSTEM_EXTENSIONS \
                      if hook['enabled'])
    for extensionmanager in HOOK_POINTS.itervalues():
        hooks = extensionmanager.findExtensionInfo(warn_old_extensions=False)
        for hook in hooks:
            if hook['qlocation'] not in known_hooks and \
                hook['qlocation'].startswith(extensionmanager.hook_base_name) and \
                hook['qlocation'] == qlocation:
                extensionmanager.populateExtension(hook['extension_path'], hook)
