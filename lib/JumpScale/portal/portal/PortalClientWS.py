from JumpScale import j
import re

CONTENT_TYPE_JSON = 'application/json'

class PortalClientWS():

    def __init__(self, ip, port, secret=None):
        self.ip = ip
        self.port = port
        self.secret = secret
        import JumpScale.baselib.http_client
        self.httpconnection = j.clients.http.getConnection()

    def html2text(self, data):
        # get only the body content
        bodyPat = re.compile(r'< body[^<>]*?>(.*?)< / body >', re.I)
        result = re.findall(bodyPat, data)
        if len(result) > 0:
            data = result[0]

        # now remove the java script
        p = re.compile(r'< script[^<>]*?>.*?< / script >')
        data = p.sub('', data)

        # remove the css styles
        p = re.compile(r'< style[^<>]*?>.*?< / style >')
        data = p.sub('', data)

        # remove html comments
        p = re.compile(r'')
        data = p.sub('', data)

        # remove all the tags
        p = re.compile(r'<[^<]*?>')
        data = p.sub('', data)

        data = data.replace("&nbsp;", " ")
        data = data.replace("\n\n", "\n")

        return data

    def ping(self, nrping=1):
        url = "http://%s:%s/ping/" % (self.ip, self.port)
        for nr in range(nrping):
            result = self.httpconnection.get(url)
            result = result.read()
            if result != "ping":
                raise RuntimeError("ping error to %s %s" % (self.ip, self.port))

    def callWebService(self, appname, actorname, method, **params):
        """
        ip,port & secret are params of webservice to call
        @params the extra params is what will be passed to the webservice as arguments
            e.g. name="kds",color="red"
        @return 0, result #if ok
        @return 1, result #if error
        @return 3, result #if asyncresult
        """
        scheme = "http" if self.port != 443 else "https"
        url = "%s://%s:%s/restmachine/%s/%s/%s?authkey=%s" % (scheme, self.ip, self.port, appname, actorname, method, self.secret)
        j.logger.log("Calling URL %s" % url, 8)
        if "params" in params:
            for key in params["params"]:
                params[key] = params["params"][key]
            params.pop("params")
        #params["caller"] = j.core.grid.config.whoami

        data = j.db.serializers.getSerializerType('j').dumps(params)

        headers = {'content-type': 'application/json'}

        result = self.httpconnection.post(url, headers=headers, data=data)

        contentType = result.headers['Content-Type']
        content = result.read()

        # j.logger.log("Received result %s" % content, 8)

        if contentType == CONTENT_TYPE_JSON:
            decodedResult = j.db.serializers.getSerializerType('j').loads(content)
        else:
            raise ValueError("Cannot handle content type %s" % contentType)

        if isinstance(decodedResult, basestring):
            if decodedResult.find("ERROR: PLEASE SPECIFY PARAM") != -1:
                raise RuntimeError(self.html2text(decodedResult))
            elif decodedResult.startswith("ASYNC::"):
                r = int(decodedResult.split("::", 1)[1])
                return 3, r
            elif decodedResult.startswith("ERRORJSON::"):
                r = decodedResult.split("\n", 1)[1]  # remove first line
                return 1, j.db.serializers.getSerializerType('j').loads(r)
            elif decodedResult.startswith("ERROR::"):
                raise RuntimeError("ERROR SHOULD HAVE BEEN IN JSON FORMAT.\n%s" % self.html2text(decodedResult))

        return 0, decodedResult

