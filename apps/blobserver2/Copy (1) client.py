import tempfile
import tarfile

from JumpScale import j

# import JumpScale.grid.zdaemon
# import JumpScale.baselib.blobstor2

j.application.start("jumpscale:blobserver2test")

j.logger.consoleloglevel = 5

namespace="test"
domain="adomain"
blobstorconnection="default"

# import requests
# print 1
# for i in range(1000):
#     r = requests.get('http://localhost:8767/SET/hello/world')
#     r.json()
    
# print 2

# j.application.stop()


# from geventhttpclient import HTTPClient
# from geventhttpclient.url import URL

# url = URL('http://localhost:8767/SET/hello/world')

# http = HTTPClient("localhost",port=8767)

# print 1
# for i in range(1000):
#     # r=http.post("localhost:8767","SET/hello/world",{})
#     response = http.get("SET/hello/world")
#     from IPython import embed
#     print "DEBUG NOW s"
#     embed()
#     p
    
# print 2

# j.application.stop()

# # issue a get request
# response = http.get("SET/hello/world")

# # read status_code
# response.status_code

# # read response body
# body = response.read()

# from IPython import embed
# print "DEBUG NOW ooo"
# embed()


# # close connections
# http.close()

def test1():
    client = j.clients.blobstor2.getClient(blobstorconnection,domain,namespace)

    blob=""
    for i in range(1024*1024*4):
        blob+="A"
    #4MB
    key = j.tools.hash.md5_string(blob)

    client.set(key, blob)
    blobret=client.get(key)

    assert blobret==blob

test1()

def test2():
    client = j.clients.blobstor2.getClient(namespace,login=login, passwd=passwd)

    client2 = j.clients.blobstor2.getClient(namespace, port=2346, login=login, passwd=passwd)


    client.deleteNamespace()

    print "start"

    blob_missing = client.get(hash2)
    print "CHECKING MISSING BLOB"
    assert blob_missing == blob2 , "MISSING BLOB CANNOT BE FOUND"

    print "SUCCESS"

    client.set(hash, blob, repoId="repo1")
    client.set(hash, blob, repoId="repo2")

    blob2 = client.get(hash)

    assert blob2==blob

    md = client.getMD(hash)
    print md

    blob2 = client.delete(hash, repoId="repo1")

    md = client.getMD(hash)
    print md

    assert client.exists(hash, repoId="repo2")==True
    assert client.exists(hash, repoId="repo1")==False
    assert client.exists(hash)==True

    blob2 = client.delete(hash, repoId="repo2")
    assert client.exists(hash)==False

    # TESTING Blob Patches

    print "TESTING BLOB PATCH"
    client.deleteNamespace()

    blob = "THIS IS A BLOB"
    hash = j.tools.hash.md5_string(blob)

    # Set the Blob
    client.set(hash, blob)

    keyList = [hash]
    blob_tar = client.getBlobPatch(keyList)

    blob_patch = tempfile.mktemp(prefix="blob_", suffix=".tar")
    j.system.fs.writeFile(blob_patch, blob_tar)

    blob_target = tempfile.mkdtemp(prefix="blobtarget_")
    tar = tarfile.open(blob_patch)
    tar.extractall(path=blob_target)
    tar.close()

    print "DONE!"

j.application.stop()

