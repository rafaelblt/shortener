from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from shortener.domain.shared import PaginatedResult
from shortener.domain.user import User, UserRepository
from shortener.domain.user.fields import Email, Name, HashedPassword
from shortener.domain.user.exceptions import (
    UserNotFoundInDatabaseError, UserInvalidToUpdateError
)

from shortener.infra.db.mappers import (
    map_user_model_to_domain, map_user_domain_to_model
)
from shortener.infra.db.models import UserModel, ShortURLModel


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository."""

    def __init__(self, session: AsyncSession):
        """
        Args:
            session (Session): SQLAlchemy Async Session instance.
        """
        self.session = session

    async def add(self, user: User) -> User:
        model = self._to_model(user)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def update(self, user: User) -> User:
        if user.id is None:
            raise UserInvalidToUpdateError("User needs a ID to update")

        existing_model = await self._get_model_by_id(user.id)

        if existing_model is None:
            raise UserNotFoundInDatabaseError(
                f"User with id={user.id} not found in database."
            )

        existing_model.email = user.email
        existing_model.name = user.name
        existing_model.hashed_password = user.hashed_password
        existing_model.status = user.status
        # TODO: update model.shorturls
        existing_model.is_superuser = user.is_superuser
        existing_model.created_at = user.created_at
        existing_model.last_login = user.last_login

        await self.session.commit()
        await self.session.refresh(existing_model)

        return self._to_domain(existing_model)

    async def get_all(self) -> list[User]:
        models = await self._get_all_models()
        return [self._to_domain(model) for model in models]

    async def get_by_id(self, id: int) -> User | None:
        model = await self._get_model_by_id(id)
        return self._to_domain(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        model = await self._get_model_by_email(email)
        return self._to_domain(model) if model else None

    async def list_paginated(self, offset: int, limit: int):
        total = await self.session.scalar(
            select(func.count()).select_from(UserModel)
        )
        rows = await self.session.scalars(
            select(UserModel)
            .offset(offset)
            .limit(limit)
        )
        entities = [self._to_domain(m) for m in rows.all()]
        return PaginatedResult(entities, total, offset, limit)

    async def exists_by_email(self, email: str) -> bool:
        """
        Checks if a User exists by its email.

        Args:
            email (str): The User email.

        Returns:
            bool: True if a User with the given email exists, False otherwise.
        """
        model = await self._get_model_by_email(email)
        return model is not None

    async def delete_by_id(self, id: int) -> User:
        model = await self._get_model_by_id(id)
        if model is None:
            raise UserNotFoundInDatabaseError(
                f"User with id={id} not found in database."
            )

        await self.session.delete(model)
        await self.session.commit()
        return self._to_domain(model)

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

    def _to_domain(model: UserModel) -> User:
        """Converts a SQLAlchemy model instance to a domain entity."""
        return map_user_model_to_domain(model)

    def _to_model(self, entity: User) -> UserModel:
        """Converts a domain entity to a SQLAlchemy model instance."""
        return map_user_domain_to_model(entity)