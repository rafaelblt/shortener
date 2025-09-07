from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from shortener.domain.shared import PaginatedResult
from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.user import User, UserRepository
from shortener.domain.user.exceptions import UserNotFoundError

from shortener.infra.db.mappers import UserMapper
from shortener.infra.db.models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository."""

    def __init__(self, session: AsyncSession):
        """
        Args:
            session (Session): SQLAlchemy Async Session instance.
        """
        self.session = session
        self.mapper = UserMapper(session)

    async def add(self, user: User) -> User:
        model = await self._to_model(user)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return await self._to_domain(model)

    async def update(self, user: User) -> User:
        user_id = user.pk.get_id()

        existing_model = await self._get_model_by_id(user_id)
        if existing_model is None:
            raise UserNotFoundError(value=user.pk, field="pk")

        existing_model.email = user.email
        existing_model.name = user.name
        existing_model.hashed_password = user.hashed_password
        existing_model.plan_id = user.plan.pk.get_id()
        existing_model.status = user.status
        existing_model.is_superuser = user.is_superuser
        existing_model.created_at = user.created_at
        existing_model.last_login = user.last_login

        await self.session.commit()
        await self.session.refresh(existing_model)

        return await self._to_domain(existing_model)

    async def get_all(self) -> list[User]:
        models = await self._get_all_models()
        return [await self._to_domain(model) for model in models]

    async def get_by_pk(self, pk: PrimaryKey) -> User | None:
        if not pk.is_id():
            return None
        id = pk.get_id()
        model = await self._get_model_by_id(id)
        return await self._to_domain(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        model = await self._get_model_by_email(email)
        return await self._to_domain(model) if model else None

    async def list_paginated(self, offset: int, limit: int):
        total = await self.session.scalar(
            select(func.count()).select_from(UserModel)
        )
        total = total or 0
        rows = await self.session.scalars(
            select(UserModel)
            .offset(offset)
            .limit(limit)
        )
        entities = [await self._to_domain(m) for m in rows.all()]
        return PaginatedResult(entities, total, offset, limit)

    async def exists_by_email(self, email: str) -> bool:
        model = await self._get_model_by_email(email)
        return model is not None

    async def delete_by_pk(self, pk: PrimaryKey) -> User:
        model = await self._get_model_by_id(pk.get_id())
        if model is None:
            raise UserNotFoundError(value=pk, field="pk")

        domain = await self._to_domain(model)

        await self.session.delete(model)
        await self.session.commit()
        return domain

    async def _get_all_models(self) -> Sequence[UserModel]:
        result = await self.session.scalars(select(UserModel))
        return result.all()

    async def _get_model_by_id(self, id: int) -> UserModel | None:
        """
        Retrieves a UserModel by its id.

        Args:
            id (int): The UserModel id.

        Returns:
            Optional[UserModel]: The model object or None if not found.
        """
        model = await self.session.get(UserModel, id)
        return model

    async def _get_model_by_email(self, email: str) -> UserModel | None:
        """
        Retrieves a UserModel by its email.

        Args:
            email (str): The UserModel email.

        Returns:
            Optional[UserModel]: The model object or None if not found.
        """
        model = await self.session.scalar(
            select(UserModel).where(UserModel.email == email)
        )
        return model

    async def _to_domain(self, model: UserModel) -> User:
        """Converts a SQLAlchemy model instance to a domain entity."""
        return await self.mapper.model_to_domain(model)

    async def _to_model(self, entity: User) -> UserModel:
        """Converts a domain entity to a SQLAlchemy model instance."""
        return await self.mapper.domain_to_model(entity)
