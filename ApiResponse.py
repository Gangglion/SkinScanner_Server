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
        """API 응답 성공 시 Return 하는 Data Object"""
        response = ApiResponse.TEMPLATE.copy()
        response["isSuccess"] = True
        response["message"] = message
        response["data"] = data
        return response, HTTPStatus.OK
    
    @staticmethod
    def error(message="An error Occurred", status_code=HTTPStatus.BAD_REQUEST):
        """API 에러 시 Return 하는 Data Object"""
        response = ApiResponse.TEMPLATE.copy()
        response["isSuccess"] = False
        response["message"] = message
        response["data"] = None
        return response, status_code
        
    @staticmethod
    def not_found(message="Resource not found"):
        """404 에러 시 Return 하는 Data Object"""
        return ApiResponse.error(message=message, status_code=HTTPStatus.NOT_FOUND)