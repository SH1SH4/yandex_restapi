from flask import Flask, request
from json import loads, dumps


def json_validator():
    try:
        data = loads(request.get_data())
        assert isinstance(data, dict)
        return data
    except Exception:
        response = Flask.response_class(
            status=400,
            response=dumps({"error_description": "Invalid JSON"}),
            mimetype='application/json')
        return response