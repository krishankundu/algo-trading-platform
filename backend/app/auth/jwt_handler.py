from jose import jwt, JWTError
from fastapi import HTTPException

SECRET_KEY = "your_secret_key"

ALGORITHM = "HS256"

def verify_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )