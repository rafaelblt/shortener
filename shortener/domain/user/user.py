from typing import Optional
from datetime import datetime

from shortener.domain.domain_entity import DomainEntity

from shortener.domain.shared.datetime_utils import is_utc, utc_now
from shortener.domain.shared.email import Email
from shortener.domain.shared.primarykey import PrimaryKey

from shortener.domain.plan import Plan
from shortener.domain.shorturl.shorturl import ShortURL

from .fields import Name, UserStatus, HashedPassword, InMemoryShortURLCollection, ShortURLCollection
from .exceptions import UserAttributeTypeError as AttrTypeError
from .exceptions import *


class User(DomainEntity):

    @staticmethod
    def get_fields() -> list[str]:
        return [
            "pk",
            "email",
            "name",
            "hashed_password",
            "plan",
            "shorturls",
            "status",
            "is_superuser",
            "created_at",
            "last_login"
        ]

    def __init__(
        self,
        email: Email,
        name: Name,
        hashed_password: HashedPassword,
        plan: Plan,
        pk: Optional[PrimaryKey] = None,
        shorturls: Optional[ShortURLCollection] = None,
        status: UserStatus = UserStatus.ACTIVE,
        is_superuser: bool = False,
        created_at: Optional[datetime] = None,
        last_login: Optional[datetime] = None
    ):
        pk = pk or PrimaryKey.create_pk_undefined()
        shorturls = shorturls or InMemoryShortURLCollection()
        created_at = created_at or utc_now()

        self.validate_pk(pk)
        self.validate_name(name)
        self.validate_email(email)
        self.validate_hashed_password(hashed_password)
        self.validate_plan(plan)
        self.validate_shorturls(shorturls)
        self.validate_status(status)
        self.validate_is_superuser(is_superuser)
        self.validate_created_at(created_at)
        self.validate_last_login(last_login)

        self._pk = pk
        self._name = name
        self._email = email
        self._hashed_password = hashed_password
        self._plan = plan
        self._shorturls = shorturls
        self._status = status
        self._is_superuser = is_superuser
        self._created_at = created_at
        self._last_login = last_login

    
    @property
    def pk(self):
        return self._pk
    
    @property
    def name(self):
        return self._name
    
    @property
    def email(self):
        return self._email
    
    @property
    def hashed_password(self):
        return self._hashed_password

    @property
    def plan(self):
        return self._plan
    
    @property
    def shorturls_collection(self) -> ShortURLCollection:
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
    def validate_pk(pk):
        if not isinstance(pk, PrimaryKey):
            raise AttrTypeError(attr="pk", type_expected="PrimaryKey", got=pk)
    
    @staticmethod
    def validate_name(name):
        if not isinstance(name, Name):
            raise AttrTypeError(attr="name", type_expected="Name", got=name)
    
    @staticmethod
    def validate_email(email):
        if not isinstance(email, Email):
            raise AttrTypeError(attr="email", type_expected="Email", got=email)
    
    @staticmethod
    def validate_hashed_password(hashed_password):
        if not isinstance(hashed_password, HashedPassword):
            raise AttrTypeError(
                attr="hashed_password",
                type_expected="HashedPassword",
                got=hashed_password
            )
    
    @staticmethod
    def validate_plan(plan):
        if not isinstance(plan, Plan):
            raise AttrTypeError(attr="plan", type_expected="Plan", got=plan)
        
    @staticmethod
    def validate_shorturls(shorturls):
        if not isinstance(shorturls, ShortURLCollection):
            raise AttrTypeError(
                attr="shorturls", type_expected="ShortURLCollection", got=shorturls
            )
    
    @staticmethod
    def validate_status(status):
        if not isinstance(status, UserStatus):
            raise AttrTypeError(
                attr="status", type_expected="UserStatus", got=status
            )
    
    @staticmethod
    def validate_is_superuser(is_superuser):
        if not isinstance(is_superuser, bool):
            raise AttrTypeError(
                attr="is_superuser", type_expected="bool", got=is_superuser
            )
    
    @staticmethod
    def validate_created_at(created_at):
        if not isinstance(created_at, datetime):
            raise AttrTypeError(
                attr="created_at", type_expected="datetime", got=created_at
            )
        if not is_utc(created_at):
            raise ValueError(
                "The User created_at datetime must be in UTC timezone."
            )
            
    @staticmethod 
    def validate_last_login(last_login):
        if not isinstance(last_login, (datetime, type(None))):
            raise AttrTypeError(
                attr="last_login", type_expected="datetime or None", got=last_login
            )
        if isinstance(last_login, datetime) and not is_utc(last_login):
            raise ValueError(
                "The User last_login datetime must be in UTC timezone."
            )
    
    
    def verify_email(self) -> None:
        """
        Checks if the user can verify their email and updates the status to 
        ACTIVE.

        Returns:
            None: The user status is updated to ACTIVE.

        Raises:
            UserStatusInvalidToVerifyEmailError: If the user status is not 
                UNVERIFIED_EMAIL.
        """
        if self.status != UserStatus.UNVERIFIED_EMAIL:
            raise UserStatusInvalidToVerifyEmailError(
                status=self.status, required_status=UserStatus.UNVERIFIED_EMAIL
            )
        self._status = UserStatus.ACTIVE

    def ensure_can_login(self) -> None:
        """
        Checks if the user is allowed to login based on their status.
        
        Returns:
            None: The user can login.

        Raises:
            UserEmailNotVerifiedError: The email has not been verified.
            UserSuspendedError: The user has been suspended.
            UserLockedError: The user has been locked.
            UserBannedError: The user has been banned.
        """
        if self.status == UserStatus.UNVERIFIED_EMAIL:
            raise UserEmailNotVerifiedError()
        elif self.status == UserStatus.SUSPENDED:
            raise UserSuspendedError()
        elif self.status == UserStatus.LOCKED:
            raise UserLockedError()
        elif self.status == UserStatus.BANNED:
            raise UserBannedError()


    async def add_shorturl(self, shorturl: ShortURL) -> None:
        if not shorturl.owner_pk.is_undefined():
            raise ShortURLAlreadyOwnedError(shorturl.owner_pk)
        if await self._shorturls.count() >= self.plan.max_shorturls:
            raise ShortURLLimitReachedError(self.plan.max_shorturls)
        await self._shorturls.add(shorturl)
        shorturl.change_owner_pk(self.pk)

    async def remove_shorturl(self, shorturl: ShortURL):
        return await self._shorturls.remove_by_pk(shorturl.pk)


    async def get_shorturls(self):
        return await self._shorturls.get_all()


    def change_name(self, new_name: Name):
        self.validate_name(new_name)
        self._name = new_name

    def change_hashed_password(self, new_hashed_password: HashedPassword):
        self.validate_hashed_password(new_hashed_password)
        self._hashed_password = new_hashed_password

    def change_plan(self, new_plan: Plan):
        self.validate_plan(new_plan)
        self._plan = new_plan


    def update_last_login(self):
        """Updates the last_login attribute to the current UTC datetime."""
        self._last_login = utc_now()


    def __repr__(self):
        return f"<User pk={self.pk} email={self.email} name={self.name}>"
