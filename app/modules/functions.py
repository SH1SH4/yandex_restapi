from flask import Flask, request
from json import loads, dumps, JSONDecodeError


def json_validator():
    try:
        data = loads(request.get_data())
        assert isinstance(data, dict)
        assert data
        return data
    except Exception as e:
        print(e)
        response = Flask.response_class(
            status=400,
            response=dumps({"error_description": "Invalid JSON"}),
            mimetype='application/json')
        return response