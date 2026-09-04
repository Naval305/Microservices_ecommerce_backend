from typing import Any

from flask import Response, jsonify, make_response


class CustomResponse:
    @staticmethod
    def success(data: Any = None, message: str = "Success", status_code: int = 200) -> Response:
        response_data: dict[str, object] = {
            "status": "success",
            "message": message,
            "data": data,
        }
        return make_response(jsonify(response_data), status_code)

    @staticmethod
    def error(
        message: str = "Error",
        status_code: int = 400,
        code: str = "error",
        errors: Any = None,
    ) -> Response:
        response_data: dict[str, object] = {
            "status": "error",
            "code": code,
            "message": message,
        }
        if errors is not None:
            response_data["errors"] = errors
        return make_response(jsonify(response_data), status_code)
