# API Response
from http import HTTPStatus

class ApiResponse:
    TEMPLATE = {
        "isSuccess" : None,
        "message" : None,
        "data" : None
    }
    
    @staticmethod
    def success(data=None, message="Success"):
        response = ApiResponse.TEMPLATE.copy()
        response["isSuccess"] = True
        response["message"] = message
        response["data"] = data
        return response, HTTPStatus.OK
    
    @staticmethod
    def error(message="An error Occurred", status_code=HTTPStatus.BAD_REQUEST):
        response = ApiResponse.TEMPLATE.copy()
        response["isSuccess"] = False
        response["message"] = message
        response["data"] = None
        return response, status_code
        
    @staticmethod
    def not_found(message="Resource not found"):
        return ApiResponse.error(message=message, status_code=HTTPStatus.NOT_FOUND)