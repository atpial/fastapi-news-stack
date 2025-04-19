from pydantic import BaseModel


class TokenRequest(BaseModel):
    client_id: str
    client_secret: str
