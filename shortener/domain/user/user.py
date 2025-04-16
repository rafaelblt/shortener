from datetime import datetime, timezone
from typing import Optional

from .fields import Email, Name, UserStatus, HashedPassword
from .exceptions import UserAttributeTypeError


class User:
    def __init__(
        self,
        email: Email,
        name: Name,
        hashed_password: str = "",
        id: Optional[int] = None,
        shorturls: list = [],
        status: UserStatus = UserStatus.ACTIVE,
        is_superuser: bool = False,
        created_at: Optional[datetime] = None,
        last_login: Optional[datetime] = None
    ):
        created_at = created_at or datetime.now(tz=timezone.utc)

        self.validate_id(id)
        self.validate_name(name)
        self.validate_email(email)
        self.validate_hashed_password(hashed_password)
        self.validate_shorturls(shorturls)
        self.validate_status(status)
        self.validate_is_superuser(is_superuser)
        self.validate_created_at(created_at)
        self.validate_last_login(last_login)

        self._id = id
        self._name = name
        self._email = email
        self._hashed_password = hashed_password
        self._shorturls = shorturls
        self._status = status
        self._is_superuser = is_superuser
        self._created_at = created_at
        self._last_login = last_login

    
    @property
    def id(self):
        return self._id
    
    @property
    def name(self):
        return self._name
    
    @property.setter
    def name(self, name):
        self.validate_name(name)
        self._name = name
    
    @property
    def email(self):
        return self._email
    
    @property
    def hashed_password(self):
        return self._hashed_password
    
    @property
    def shorturls(self):
        from shortener.domain.shorturl import ShortURL
        self._shorturls: list[ShortURL]
        return self._shorturls
    
    @property
    def status(self):
        return self._status
    
    @property
    def is_superuser(self):
        return self._is_superuser

    @property
    def created_at(self):
        return self._created_at
    
    @property
    def last_login(self):
        return self._last_login


    @staticmethod
    def validate_id(id):
        if not isinstance(id, (int, type(None))):
            raise UserAttributeTypeError(
                attr="id", type_expected="int or None", got=id
            )
    
    @staticmethod
    def validate_name(name):
        if not isinstance(name, Name):
            raise UserAttributeTypeError(
                attr="name", type_expected="Name", got=name
            )
    
    @staticmethod
    def validate_email(email):
        if not isinstance(email, Email):
            raise UserAttributeTypeError(
                attr="email", type_expected="Email", got=email
            )
    
    @staticmethod
    def validate_hashed_password(hashed_password):
        if not isinstance(hashed_password, HashedPassword):
            raise UserAttributeTypeError(
                attr="hashed_password", type_expected="HashedPassword", 
                got=hashed_password
            )
    
    @staticmethod
    def validate_shorturls(shorturls):
        if not isinstance(shorturls, list):
            raise UserAttributeTypeError(
                attr="shorturls", type_expected="list", got=shorturls
            )
    
    @staticmethod
    def validate_status(status):
        if not isinstance(status, UserStatus):
            raise UserAttributeTypeError(
                attr="status", type_expected="UserStatus", got=status
            )
    
    @staticmethod
    def validate_is_superuser(is_superuser):
        if not isinstance(is_superuser, bool):
            raise UserAttributeTypeError(
                attr="is_superuser", type_expected="bool", got=is_superuser
            )
    
    @staticmethod
    def validate_created_at(created_at):
        if not isinstance(created_at, datetime):
            raise UserAttributeTypeError(
                attr="created_at", type_expected="datetime", got=created_at
            )
    
    @staticmethod 
    def validate_last_login(last_login):
        if not isinstance(last_login, (datetime, type(None))):
            raise UserAttributeTypeError(
                attr="last_login", type_expected="datetime or None", got=last_login
            )


    def __repr__(self):
        return (f"<User id={self.id} email={self.email} name={self.name} "
                f"hashed_password={self.hashed_password} shorturls={self.shorturls} "
                f"status={self.status} is_superuser={self.is_superuser} "
                f"created_at={self.created_at} las_login={self.last_login}>")
