from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from app.config import settings
from app.global_utils import get_response

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        print(f"Decoded payload: {payload}")
        return get_response(
            data=payload,
            message="Token verified successfully",
            status=status.HTTP_200_OK,
            error=False,
            code="TOKEN_VERIFIED",
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
