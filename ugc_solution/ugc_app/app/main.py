import logging
import os
import sys

import uvicorn
from fastapi import FastAPI

from app.api.v1 import endpoints, service
from app.core.logger import LOGGING

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__))))
)
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    )
)


app = FastAPI()

app.include_router(service.router, tags=["service"])
app.include_router(endpoints.router, prefix="/api/v1", tags=["endpoints"])


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
