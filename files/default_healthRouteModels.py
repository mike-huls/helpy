from pydantic import BaseModel, validator


class ResponseModel(BaseModel):
    response: str

    @validator('response')
    def validate_type(cls, response:str):
        return response.capitalize()

class InputModel(BaseModel):
    name: str
