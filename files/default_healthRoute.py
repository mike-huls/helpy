from fastapi import APIRouter
from .healthRouteModels import InputModel, ResponseModel

router_health = APIRouter()


@router_health.get(path="/api", status_code=200, )
def api_is_up():
    """ Status of the API """

    return "up"



@router_health.post(
    path="/example",                              # path where route is available
    # description="default description",            # optional: set route description here or in docstring of function of this decorator
    include_in_schema=True,                       # optional (default True). Set False to hide this route in Swagger
    # summary="This is the Swagger summary",        # optional: set here or by the name of the function of this decorator (example_request)
    status_code=200,                              # optional default response status code
    response_model=ResponseModel,                 # optional response model: api user can expect the API to return this type
    response_description="Response description",  # optional description of the response
)
def example_request(body:InputModel, age:int=None):
    """ This how you add a description in Swagger. This is plain markdown (md).<br>
        In this example we have to pass a payload of type InputModel and an optional parameter 'age' of type int

        We can also make codeblocks:
        ```python
        greeting = "hello"
        print(greeting)
        ```

        You can even add a list
        * Point 1
        * Point 2
            * Point 2.1 with some extra explanation
    """
    response = f"hello {body.name}"
    if (age != None):
        response += f" (age {age})"

    return ResponseModel(response=response)


