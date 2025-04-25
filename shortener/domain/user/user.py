from datetime import datetime
from typing import Optional

from shortener.domain.shared.datetime_utils import is_utc, utc_now
from shortener.domain.plan import Plan

from .fields import Email, Name, UserStatus, HashedPassword
from .exceptions import UserAttributeTypeError as AttrTypeError


class User:
    def __init__(
        self,
        email: Email,
        name: Name,
        hashed_password: HashedPassword,
        plan: Plan,
        id: Optional[int] = None,
        shorturls_count: int = 0,
        status: UserStatus = UserStatus.ACTIVE,
        is_superuser: bool = False,
        created_at: Optional[datetime] = None,
        last_login: Optional[datetime] = None
    ):
        created_at = created_at or utc_now()

        self.validate_id(id)
        self.validate_name(name)
        self.validate_email(email)
        self.validate_hashed_password(hashed_password)
        self.validate_plan(plan)
        self.validate_shorturls_count(shorturls_count)
        self.validate_status(status)
        self.validate_is_superuser(is_superuser)
        self.validate_created_at(created_at)
        self.validate_last_login(last_login)

        self._id = id
        self._name = name
        self._email = email
        self._hashed_password = hashed_password
        self._plan = plan
        self._shorturls_count = shorturls_count
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
    
    @name.setter
    def name(self, name):
        self.validate_name(name)
        self._name = name
    
    @property
    def email(self):
        return self._email
    
    @property
    def hashed_password(self):
        return self._hashed_password
    
    @hashed_password.setter
    def hashed_password(self, hashed_password):
        self.validate_hashed_password(hashed_password)
        self._hashed_password = hashed_password

    @property
    def plan(self):
        return self._plan
    
    @property
    def shorturls_count(self):
        return self._shorturls_count
    
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
            raise AttrTypeError(attr="id", type_expected="int or None", got=id)
    
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
    def validate_shorturls_count(shorturls_count):
        if not isinstance(shorturls_count, int):
            raise AttrTypeError(
                attr="shorturls_count", type_expected="int", got=shorturls_count
            )
        if shorturls_count < 0:
            raise ValueError(
                ("The User shorturls_count must be greater than or equal to 0, "
                f"got {shorturls_count}")
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
        if isinstance(created_at, datetime) and not is_utc(created_at):
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
    

    def update_last_login(self):
        self._last_login = utc_now()


    def __repr__(self):
        return (f"<User id={self.id} email={self.email} name={self.name} "
                f"hashed_password={self.hashed_password} shorturls={self.shorturls} "
                f"status={self.status} is_superuser={self.is_superuser} "
                f"created_at={self.created_at} last_login={self.last_login}>")
