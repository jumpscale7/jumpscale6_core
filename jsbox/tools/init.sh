#!/bin/bash
rm -rf /etc/jumpscale
ln -s /opt/jsbox/tools/init/jumpscale/ /etc/jumpscale
rm -rf /usr/local/bin/js
rm -rf /usr/local/bin/jpackage
#rm -rf /usr/local/bin/jscode
ln -s /opt/jsbox/tools/js /usr/local/bin/js
#ln -s /opt/jsbox/tools/jpackage /usr/local/bin/jpackage
#ln -s /opt/jsbox/tools/js /usr/local/bin/jscode
