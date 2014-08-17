from JumpScale import j
j.application.start('jpackages')


# jp= j.packages.findNewest(name="all")

jp= j.packages.findNewest(name="agentcontroller")

# print jp.getDependencies()

# recipe=jp.getCodeMgmtRecipe()
# print recipe
# jp.package(dependencies=False)

# jp.codeLink()
# jp.codeExport()

# print "getcodelocations"
# print "\n".join(jp.getCodeLocationsFromRecipe())
# print

# print "dependencies"
# for item in jp.getDependencies():
#     print "%s"%item

# for platform,ttype in jp.getBlobPlatformTypes():
#     for md5,path in jp.getBlobInfo(platform,ttype):
#         jpackageFilesPath,destpathOnSystem=jp.getBlobItemPaths(platform,ttype,path)
#         print "%s\n    %s\n        %s"%(md5,jpackageFilesPath,destpathOnSystem)

# jp.upload()
#jp.download()


for jp in j.packages.getJPackageObjects():
    jp.clean()

j.application.stop()
