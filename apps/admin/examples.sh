
#first clean environment
#deploy on 1 node, force reinstall, do first upload from etc, then update platform, then install jumpscale, then configure jumpscale & platform
jsadmin exec  -p R00t3r -r m4pub -c basemachine_nogrid -n clean,uploadetc,platform,coredebug,configure -f

jsadmin exec  -p R00t3r -c basemachine_nogrid -n uploadetc -f
jsadmin exec  -p R00t3r -c basemachine_nogrid -n securitydeploy  -r m4pub

jsadmin exec  -p R00t3r -r m4pub -c basemachine_nogrid -n clean,uploadetc,platform,coredebug,configure,securitydeploy -f

jsadmin exec  -p R00t3r -r m4pub -c basemachine_nogrid -n configure,-f


#create ftp connection to jsftp
#curlftpfs ftp://root:???@192.198.94.5:2111/ /mnt/ws/




