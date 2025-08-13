from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shortener.domain.refresh_token import RefreshToken, RefreshTokenRepository

from shortener.domain.refresh_token.exceptions import RefreshTokenNotFoundError
from shortener.domain.shared.primarykey import PrimaryKey

from shortener.infra.db.models import RefreshTokenModel
from shortener.infra.db.mappers import (
    map_refresh_token_domain_to_model, map_refresh_token_model_to_domain
)


class SQLAlchemyRefreshTokenRepository(RefreshTokenRepository):
    """SQLAlchemy implementation of RefreshTokenRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, refresh_token: RefreshToken) -> RefreshToken:
        model = self._to_model(refresh_token)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_domain(model)
    
    async def update(self, refresh_token: RefreshToken) -> RefreshToken:
        refresh_token_id = refresh_token.pk.get_id()

        existing_model = await self._get_model_by_id(refresh_token_id)
        if existing_model is None:
            raise RefreshTokenNotFoundError(value=refresh_token.pk, field="pk")
        
        existing_model.token = refresh_token.token
        existing_model.user_id = refresh_token.user.pk.get_id()
        existing_model.expires_at = refresh_token.expires_at
        existing_model.created_at = refresh_token.created_at
        existing_model.revoked = refresh_token.revoked

        await self.session.commit()
        await self.session.refresh(existing_model)

        return self._to_domain(existing_model)

    async def get_by_pk(self, pk: PrimaryKey) -> RefreshToken | None:
        if not pk.is_id():
            return None
        id = pk.get_id()
        model = await self._get_model_by_id(id)
        return self._to_domain(model) if model else None
    
    async def get_by_token(self, token: str) -> RefreshToken | None:
        model = await self.session.scalar(
            select(RefreshTokenModel).where(RefreshTokenModel.token == token)
        )
        return self._to_domain(model) if model else None
    
    async def _get_all_models(self) -> Sequence[RefreshTokenModel]:
        result = await self.session.scalars(select(RefreshTokenModel))
        return result.all()

    async def _get_model_by_id(self, id: int) -> RefreshTokenModel | None:
        model = await self.session.get(RefreshTokenModel, id)
        return model

    def _to_domain(self, model: RefreshTokenModel) -> RefreshToken:
        return map_refresh_token_model_to_domain(model)

    def _to_model(self, entity: RefreshToken) -> RefreshTokenModel:
        return map_refresh_token_domain_to_model(entity)
