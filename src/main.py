from litestar import Litestar,Response,Request, MediaType

from litestar.openapi import OpenAPIConfig
import uvicorn

from backend.api_gpt import ApiGpt
from backend.test import Test
from backend.actor import Actor


def value_error_handler(request: Request, exc: ValueError) -> Response:
    return Response(
        media_type=MediaType.TEXT,
        content=f"value error: {exc}",
        status_code=400,
    )


app = Litestar(route_handlers=[ApiGpt,
                               Test,
                               Actor],
               openapi_config=OpenAPIConfig(title="Cinema BackEnd", version="1.0.0"),
               exception_handlers={ValueError: value_error_handler}
            )

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000) # in a docker host="0.0.0.0"

    # elements : 127.0.0.1/schema/elements
    # swagger : 127.0.0.1/schema/swagger
    # redoc : 127.0.0.1/schema/redoc
    # ....