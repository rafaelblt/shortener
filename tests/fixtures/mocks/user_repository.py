from shortener.domain.shared.pagination import PaginatedResult

from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.user import User, UserRepository
from shortener.domain.user.exceptions import UserNotFoundError

from .database import MockDatabase, PkManager


class MockUserRepository(UserRepository):
    def __init__(self):
        self.database = MockDatabase(index_manager=PkManager())

    async def add(self, user: User) -> User:
        user_dict = self._to_dict(user)
        user_dict = self.database.add(entity=user_dict)
        return self._to_domain(user_dict)
    
    async def update(self, user: User) -> User:
        user_dict = self.database.get_by_index(user.pk)

        if user_dict is None:
            raise UserNotFoundError(value=user.pk, field="pk") 

        user_dict["email"] = user.email
        user_dict["name"] = user.name
        user_dict["hashed_password"] = user.hashed_password
        user_dict["plan"] = user.plan
        user_dict["status"] = user.status
        user_dict["is_superuser"] = user.is_superuser
        user_dict["created_at"] = user.created_at
        user_dict["last_login"] = user.last_login

        return self._to_domain(user_dict)
    
    async def get_all(self) -> list[User]:
        return [self._to_domain(entity) for entity in self.database.get_all()]

    async def get_by_pk(self, pk: PrimaryKey) -> User | None:
        user_dict = self.database.get_by_index(pk)
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

    async def exists_by_email(self, email: str) -> bool:
        if await self.get_by_email(email):
            return True
        return False

    async def delete_by_pk(self, pk: PrimaryKey) -> User:
        user_dict = self.database.delete_by_index(pk)
        if user_dict:
            return self._to_domain(user_dict)
        raise UserNotFoundError(value=pk, field="pk")
            
    def _to_dict(self, user: User) -> dict:
        return {
            "pk": user.pk,
            "email": user.email,
            "name": user.name,
            "hashed_password": user.hashed_password,
            "plan": user.plan,
            "status": user.status,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at,
            "last_login": user.last_login
        }
    
    def _to_domain(self, user_dict: dict) -> User:
        return User(
            pk=user_dict["pk"],
            email=user_dict["email"],
            name=user_dict["name"],
            hashed_password=user_dict["hashed_password"],
            plan=user_dict["plan"],
            status=user_dict["status"],
            is_superuser=user_dict["is_superuser"],
            created_at=user_dict["created_at"],
            last_login=user_dict["last_login"]
        ) 
