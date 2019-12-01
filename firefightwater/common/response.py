import json
from django.http import HttpResponse, HttpRequest

def response_as_json(data):
    jsonString = json.dumps(data)
    response = HttpResponse(
            # json.dumps(dataa, cls=MyEncoder),
            jsonString,
            content_type="application/json",
    )
    response["Access-Control-Allow-Origin"] = "*"
    return response


def json_response(data, code=200):
    data = {
        "code": code,
        "msg": "success",
        "data": data,
    }
    return response_as_json(data)


def json_error(data="", code=500):
    data = {
        "code": code,
        "msg": "error",
        "data": data
    }
    return response_as_json(data)