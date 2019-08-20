from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.status import HTTP_401_UNAUTHORIZED

from rfhub2 import config

security = HTTPBasic()


def authenticated_user(
    user: HTTPBasicCredentials = Depends(security)
) -> HTTPBasicCredentials:
    if (
        user.username == config.BASIC_AUTH_USER
        and user.password == config.BASIC_AUTH_PASSWORD
    ):
        return user
    else:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Unauthorized to perform this action",
            headers={"WWW-Authenticate": "Basic"},
        )


def is_authenticated(user: HTTPBasicCredentials = Depends(security)) -> bool:
    return authenticated_user(user) is not None
