set -ex
#!/bin/bash
rm -rf /etc/jumpscale
rm -rf /usr/local/bin/jspython
rm -rf /usr/bin/jspython
ln -s /opt/jsbox/tools/jspython /usr/local/bin/jspython
rm -rf /usr/local/bin/js
rm -rf /usr/local/bin/jpackage
rm -rf /usr/local/bin/jscode
rm -rf /usr/local/bin/jssync
rm -rf /usr/local/bin/jsprocess
rm -rf /usr/local/bin/jsgrid
rm -rf /usr/local/bin/jsmachine
rm -rf /usr/local/bin/jsdisk
rm -rf /usr/local/bin/jsnet

ln -s /opt/jsbox/tools/js /usr/local/bin/js
ln -s /opt/jsbox/tools/jpackage /usr/local/bin/jpackage
ln -s /opt/jsbox/tools/jscode /usr/local/bin/jscode
ln -s /opt/jsbox/tools/jssync /usr/local/bin/jssync
ln -s /opt/jsbox/tools/jsprocess /usr/local/bin/jsprocess
ln -s /opt/jsbox/tools/jsgrid /usr/local/bin/jsgrid
ln -s /opt/jsbox/tools/jsmachine /usr/local/bin/jsmachine
ln -s /opt/jsbox/tools/jsdisk /usr/local/bin/jsdisk
ln -s /opt/jsbox/tools/jsnet /usr/local/bin/jsnet