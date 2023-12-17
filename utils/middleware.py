import os
from datetime import datetime
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logging.getLogger(__name__)


class LogRequestsMiddleware(BaseHTTPMiddleware):
    def __init__(
            self,
            app,
    ):
        super().__init__(app)
        self.request = Request

    async def dispatch(self, request, call_next):
        request.state.request_id = ''.join(uuid.uuid4().hex[:16])
        start_time = datetime.now()

        response = await call_next(request)

        process_time = (datetime.now() - start_time).total_seconds() * 1000
        formatted_process_time = '{0:.2f}'.format(process_time)
        logging.info(
            f"request_path={request.url.path} request_method={request.method} request_headers={request.headers} "
            f"request_body={request.body}")
        response.headers["X-Process-Time"] = str(formatted_process_time)
        response.headers["X-Request-ID"] = str(request.state.request_id)

        return response



