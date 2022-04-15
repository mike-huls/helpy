import logging

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import RedirectResponse

from routes.meta.healthRoute import router_health

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name="{API_NAME}")


app = FastAPI(
    title='{API_NAME}',
    # description='see routes below'
    version='0.0.1'
)

app.include_router(router=router_health, prefix='/health', tags=['health'])


@app.on_event("startup")
def startup():
    logger.info("Startup completed")
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"--REQUEST: {request.url.path}")
    response = await call_next(request)
    return response
@app.get("/", tags=['meta'], include_in_schema=False)
async def redirect():
    response = RedirectResponse(url='/docs')
    return response


