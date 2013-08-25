
def main(o, args, params, tags, tasklet):
    params.merge(args)

    doc = params.doc
    tags = params.tags

    out = ""
    cmdstr = params.macrostr.split(":", 1)[1].replace("}}", "").strip()
    md5 = j.base.byteprocessor.hashMd5(cmdstr)
    j.system.fs.createDir(j.system.fs.joinPaths(j.core.portal.runningPortal.webserver.filesroot, "dot"))
    path = j.system.fs.joinPaths(j.core.portal.runningPortal.webserver.filesroot, "dot", md5)
    if not j.system.fs.exists(path + ".png"):
        j.system.fs.writeFile(path + ".dot", cmdstr)
        cmd = "dot -Tpng %s.dot -o %s.png" % (path, path)

        # for i in range(5):
        rescode, result = j.system.process.execute(cmd)
            # if result.find("warning")==011:

        if result.find("warning") != -1:
            out = result
            out += '\n'
            out += "##DOT FILE WAS##:\n"
            out += cmdstr
            out += "##END OF DOT FILE##\n"
            out = "{{code:\n%s\n}}" % out

            params.result = out

            return params

    out = "!/root/dot/%s.png!" % md5

    params.result = (out, doc)

    return params


def match(o, args, params, tags, tasklet):
    return True
