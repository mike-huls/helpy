from fastapi import APIRouter


router_health = APIRouter()


@router_health.get(path="/api", status_code=200)
def api_is_up():
    """ Status of the API """

    return "up"