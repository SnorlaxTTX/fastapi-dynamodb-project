from fastapi import HTTPException, status


class ErrorCode:
    @staticmethod
    def NotFound(service_name: str, identifier: str):
        # Raising HTTPException with 404 and customized message
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{service_name} with UUID {identifier} not found."
        )

    @staticmethod
    def Conflict(service_name: str, identifier: str):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{service_name} with UUID {identifier} already exists."
        )

    @staticmethod
    def BadRequest(message: str):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    @staticmethod
    def Unauthorized(message: str):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)

    @staticmethod
    def Forbidden(message: str):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)
