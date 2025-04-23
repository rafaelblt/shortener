from shortener.domain.shared.pagination import PaginatedResult

from shortener.domain.user import User, UserRepository
from shortener.domain.user.exceptions import (
    UserInvalidToUpdateError, UserNotFoundInDatabaseError
)

from .database import MockDatabase, IdManager


class MockUserRepository(UserRepository):
    def __init__(self):
        self.database = MockDatabase(index_manager=IdManager())

    async def add(self, user: User) -> User:
        user_dict = self._to_dict(user)
        user_dict = self.database.add(entity=user_dict)
        return self._to_domain(user_dict)
    
    async def update(self, user: User) -> User:
        if user.id is None:
            raise UserInvalidToUpdateError("User needs a ID to update")
        
        if not self.database.exists_by_index(user.id):
            raise UserNotFoundInDatabaseError(
                f"User with id={user.id} not found in MockUserRepository."
            )

        user_dict = self.database.get_by_index(user.id)
        user_dict["email"] = user.email
        user_dict["name"] = user.name
        user_dict["hashed_password"] = user.hashed_password
        user_dict["plan"] = user.plan
        user_dict["shorturls"] = user.shorturls
        user_dict["status"] = user.status
        user_dict["is_superuser"] = user.is_superuser
        user_dict["created_at"] = user.created_at
        user_dict["last_login"] = user.last_login

        return self._to_domain(user_dict)
    
    async def get_all(self) -> list[User]:
        return [self._to_domain(entity) for entity in self.database.get_all()]

    async def get_by_id(self, id: int) -> User | None:
        user_dict = self.database.get_by_index(id)
        if user_dict:
            return self._to_domain(user_dict)
        return None

    async def get_by_email(self, email: str) -> User | None:
        user_dict = self.database.get_by_field(field="email", value=email)
        if user_dict:
            return self._to_domain(user_dict)
        return None
    
    async def list_paginated(self, offset, limit):
        data = await self.get_all()
        total = len(data)
        rows = list(data)[offset:offset + limit]
        return PaginatedResult(rows, total, offset, limit)

    async def exists_by_email(self, slug: str) -> bool:
        if await self.get_by_email(slug):
            return True
        return False

    async def delete_by_id(self, id: int) -> User:
        user_dict = self.database.delete_by_index(id)
        if user_dict:
            return self._to_domain(user_dict)
        raise UserNotFoundInDatabaseError(
            f"User with id={id} not found in MockUserRepository."
        )
            
    def _to_dict(self, user: User) -> dict:
        return {
            "pk": user.id,
            "email": user.email,
            "name": user.name,
            "hashed_password": user.hashed_password,
            "plan": user.plan,
            "shorturls": user.shorturls,
            "status": user.status,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at,
            "last_login": user.last_login
        }
    
    def _to_domain(self, user_dict: dict) -> User:
        return User(
            id=user_dict["pk"],
            email=user_dict["email"],
            name=user_dict["name"],
            hashed_password=user_dict["hashed_password"],
            plan=user_dict["plan"],
            shorturls=user_dict["shorturls"],
            status=user_dict["status"],
            is_superuser=user_dict["is_superuser"],
            created_at=user_dict["created_at"],
            last_login=user_dict["last_login"]
        ) 
