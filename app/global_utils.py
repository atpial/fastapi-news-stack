from fastapi.responses import JSONResponse


def get_response(
    message: str, status: int = 400, error: bool = True, code="GENERIC", data=None
):
    header = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "*",
        "Content-Type": "application/json",
    }

    response_data = {
        "message": message,
        "error": error,
        "code": code,
        "data": data,
    }

    return JSONResponse(
        content=response_data,
        status_code=status,
        headers=header,
    )
