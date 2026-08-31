from flask import jsonify, make_response


class CustomResponse:
    @staticmethod
    def success(data=None, message="Success", status_code=200):
        response_data = {
            "status": "success",
            "message": message,
            "data": data,
        }
        return make_response(jsonify(response_data), status_code)

    @staticmethod
    def error(message="Error", status_code=400, code="error", errors=None):
        response_data = {
            "status": "error",
            "code": code,
            "message": message,
        }
        if errors is not None:
            response_data["errors"] = errors
        return make_response(jsonify(response_data), status_code)
