from fastapi import HTTPException, status


class MissingAttribute(HTTPException):
    def __init__(self, attribute):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=f"{attribute} is missing")
        self.attribute = attribute


class EntityNotFound(HTTPException):
    def __init__(self, entity):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND,
                         detail=f"{entity} not found")


class UnableToCreate(HTTPException):
    def __init__(self, entity):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=f"unable to create new {entity}")


class UnableToGet(HTTPException):
    def __init__(self, entity):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=f"unable to get {entity}")


class DuplicateEntity(HTTPException):
    def __init__(self, entity):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=f"{entity} already exist")


class UnableToProcess(HTTPException):
    def __init__(self, detail):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN,
                         detail=f"unable to process {detail}. Please try again later")