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

""" Timestamp routines """

import time
import traceback

LASTTIME = 0
DELTATIME_INITIALIZED = False

class TimeIntervalUnit:
    """ Enumerator for time interval units """
    
    NANOSECONDS = -3
    MICROSECONDS = -2
    MILLISECONDS = -1
    SECONDS = 0
    MINUTES = 1
    HOURS = 2
    DAYS = 3
    WEEKS = 4
    MONTHS = 5
    YEARS = 6

def printdelta():
    """
    This is a function for source code or performance debugging.
    Call this function at every point cut in the source code
    where you want to print out a timestamp, together with the source code line
    """
    
    global LASTTIME, DELTATIME_INITIALIZED
    currenttime = time.time()
    if DELTATIME_INITIALIZED:
        print "... TIME DELTA: " + str(currenttime - LASTTIME),
        LASTTIME = currenttime
    else:
        print "... STARTING TIME MEASUREMENTS",
        LASTTIME = currenttime
        DELTATIME_INITIALIZED = True
    print " @ Source file [" + \
        traceback.extract_stack()[-2][0] + \
        "] line [" + \
        str(traceback.extract_stack()[-2][1]) + \
        "]"

def getabstime():
    """ Get string representation of absolute time in milliseconds """
    x = time.time()
    part1 = time.strftime("%a %d %b %Y, %H:%M:%S", time.localtime(x))
    part2 = ".%03d" % ((x%1)*1000)
    return part1 + part2