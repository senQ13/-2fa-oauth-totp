from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from app.config import settings
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from passlib.context import CryptContext
from pydantic import BaseModel

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class InvalidTokenError(Exception):
    """Ошибка действий в токене"""

    default_message = "Некорректный токен"

    def __init__(self, message: str | None = None):
        super().__init__(message or self.default_message)
        self.message = message or self.default_message


class TokenPayload(BaseModel):
    sub: UUID
    type: str
    exp: int
    iat: int
    jti: str | None = None
    role: str = "user"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hash: str) -> bool:
    return pwd_context.verify(password, hash)


def _now() -> datetime:
    return datetime.now(UTC)


def _create_token(payload_data: dict, expired_delta: timedelta) -> str:
    current_time = _now()
    exp = current_time + expired_delta

    payload = {**payload_data, "exp": int(exp.timestamp()), "iat": int(current_time.timestamp())}

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: UUID, role: str = "user") -> str:
    return _create_token(
        payload_data={"sub": str(user_id), "type": "access_token", "role": role},
        expired_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: UUID) -> tuple[str, str]:
    token_id = str(uuid4())
    token = _create_token(
        payload_data={"sub": str(user_id), "type": "refresh_token", "jti": token_id},
        expired_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    return token, token_id


def verify_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return TokenPayload.model_validate(payload)
    except ExpiredSignatureError as e:
        raise InvalidTokenError(message="Срок действия токена истек") from e
    except JWTError as e:
        raise InvalidTokenError(message="Некорректный или неизменяемый токен") from e
