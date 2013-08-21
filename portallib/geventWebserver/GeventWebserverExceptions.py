class HttpError(RuntimeError):
    pass

class HttpUnauthorized(HttpError):
    status = "401 Unauthorized"

class HttpForbidden(HttpError):
    status = "403 Forbidden"

class HttpBadRequest(HttpError):
    status = "400 Bad Request"

class HttpInternalServerError(HttpError):
    status = "500 Internal Server Error"
