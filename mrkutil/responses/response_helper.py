class ResponseHelper(object):
    RESPONSES = {
        "100": "Continue",
        "101": "Switching Protocols",
        "103": "Early Hints",
        "200": "OK",
        "201": "Created",
        "202": "Accepted",
        "203": "Non-Authoritative Information",
        "204": "No Content",
        "205": "Reset Content",
        "206": "Partial Content",
        "300": "Multiple Choices",
        "301": "Moved Permanently",
        "302": "Found",
        "303": "See Other",
        "304": "Not Modified",
        "307": "Temporary Redirect",
        "308": "Permanent Redirect",
        "400": "Bad Request",
        "401": "Unauthorized",
        "403": "Forbidden",
        "404": "Not Found",
        "405": "Method Not Allowed",
        "406": "Not Acceptable",
        "407": "Proxy Authentication Required",
        "408": "Request Timeout",
        "409": "Conflict",
        "410": "Gone",
        "411": "Length Required",
        "412": "Precondition Failed",
        "413": "Payload Too Large",
        "414": "URI Too Long",
        "415": "Unsupported Media Type",
        "416": "Range Not Satisfiable",
        "417": "Expectation Failed",
        "418": "I'm a teapot",
        "426": "Upgrade Required",
        "428": "Precondition Required",
        "429": "Too Many Requests",
        "431": "Request Header Fields Too Large",
        "451": "Unavailable For Legal Reasons",
        "500": "Internal Server Error",
        "501": "Not Implemented",
        "502": "Bad Gateway",
        "503": "Service Unavailable",
        "504": "Gateway Timeout",
        "505": "HTTP Version Not Supported",
        "506": "Variant Also Negotiates",
        "510": "Not Extended",
        "511": "Network Authentication Required",
    }

    @classmethod
    def get_response(cls, code, message=None, errors=None):
        new_message = message or cls.RESPONSES.get(str(code), "Default message")
        data = {
            "code": code,
            "response": {
                "message": new_message
            }
        }
        if errors:
            data["response"]["errors"] = errors
        if not isinstance(new_message, str):
            data["response"] = new_message
        return data

    # OPTIONS:
    #
    # data: {
    #     "code": 404,
    #     "response": {
    #         "message": "Whatever",
    #         "errors": {
    #             "username": "username is required"
    #         }
    #     }
    # }
    #
    # data: {
    #     "code": 200,
    #     "response": {
    #         "message": "Created"
    #     }
    # }
    #
    # data: {
    #     "code": 200,
    #     "response": user_object or list of objects
    # }
