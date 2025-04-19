from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.config import settings
from app.constants import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_TOKEN_TYPE, JWT_ALGORITHM
from app.global_utils import get_response
from app.auth.schemas import TokenRequest

router = APIRouter()


@router.post("/token")
def get_token(payload: TokenRequest):
    try:
        if (
            payload.client_id != settings.CLIENT_ID
            or payload.client_secret != settings.CLIENT_SECRET
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid client credentials",
            )

        to_encode = {
            "sub": payload.client_id,
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)
        return get_response(
            data={"access_token": token, "token_type": JWT_TOKEN_TYPE},
            message="Token generated successfully",
            status=status.HTTP_200_OK,
            error=False,
            code="TOKEN_GENERATED",
        )
    except HTTPException as e:
        raise e
    except JWTError as e:
        return get_response(
            message="Token generation failed",
            status=status.HTTP_400_BAD_REQUEST,
            error=True,
            code="TOKEN_GENERATION_FAILED",
        )
    except Exception as e:
        return get_response(
            message="An unexpected error occurred",
            status=status.HTTP_400_BAD_REQUEST,
            error=True,
            code="UNEXPECTED_ERROR",
        )
