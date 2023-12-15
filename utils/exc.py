from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from utils.responses_serializer import ErrorHandler
from main import app


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    response = []
    for error in errors:
        if error['type'] == 'value_error.jsondecode':
            res = ErrorHandler(request_id=request.state.request_id,  code=10012, msg='Invalid JSON body')
            response.append({'error': {'message': 'Invalid JSON body'}, 'status': 0})
        else:
            response.append(error)
    return JSONResponse(content=response, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
