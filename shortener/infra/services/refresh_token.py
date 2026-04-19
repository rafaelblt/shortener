import secrets

from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shortener.domain.shared.datetime_utils import utc_now, ensure_utc

from shortener.domain.user import User
from shortener.domain.services.token import (
    Token, AuthTokenService, TokenInvalidError, TokenExpiredError
)

from shortener.infra.db.models import RefreshTokenModel, UserModel
from shortener.infra.db.mappers import UserMapper


class SQLAlchemyRefreshAuthTokenService(AuthTokenService):
    def __init__(self, session: AsyncSession, expires_in: timedelta):
        self.session = session
        self.expires_in = expires_in

    async def generate_token(self, user: User) -> Token:
        now = utc_now()
        expires_at = now + self.expires_in
        token = secrets.token_urlsafe(64)
        model = RefreshTokenModel(
            token=token,
            user_id=user.pk.get_id(),
            created_at=now,
            expires_at=expires_at,
        )
        self.session.add(model)
        await self.session.flush()
        return Token(
            value=token,
            purpose="",
            created_at=now,
            expires_at=expires_at,
        )

    async def decode_token(self, token: str) -> User:
        # TODO: add RefreshTokenModel.revoked == False in where statement?
        refresh_token = await self.session.scalar(
            select(RefreshTokenModel).where(RefreshTokenModel.token == token)
        )
        if refresh_token is None or refresh_token.revoked:
            raise TokenInvalidError()
        if utc_now() > ensure_utc(refresh_token.expires_at):
            raise TokenExpiredError()
        user_model = await self.session.get(UserModel, refresh_token.user_id)
        if user_model is None:
            raise TokenInvalidError()
        refresh_token.revoked = True
        await self.session.flush()
        await self.session.refresh(user_model)
        return await UserMapper(self.session).model_to_domain(user_model)
