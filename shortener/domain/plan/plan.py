from typing import Optional

from shortener.domain.domain_entity import DomainEntity
from shortener.domain.shared.primarykey import PrimaryKey

from .exceptions import PlanAttributeTypeError


class Plan(DomainEntity):

    @staticmethod
    def get_fields():
        return [
            "name",
            "max_shorturls",
            "pk"
        ]

    def __init__(
        self,
        name: str,
        max_shorturls: int,
        pk: Optional[PrimaryKey] = None
    ):
        pk = pk or PrimaryKey.create_pk_undefined()

        self.validate_pk(pk)
        self.validate_name(name)
        self.validate_maxshorturls(max_shorturls)

        self._pk = pk
        self._name = name
        self._max_shorturls = max_shorturls
    
    
    @property
    def pk(self):
        return self._pk
    
    @property
    def name(self):
        return self._name
    
    @property
    def max_shorturls(self):
        return self._max_shorturls


    @staticmethod
    def validate_pk(pk):
        if not isinstance(pk, PrimaryKey):
            raise PlanAttributeTypeError(
                attr="pk", type_expected="PrimaryKey", got=pk
            )

    @staticmethod
    def validate_name(name):
        if not isinstance(name, str):
            raise PlanAttributeTypeError(
                attr="name", type_expected="str", got=name
            )
        
    @staticmethod
    def validate_maxshorturls(max_shorturls):
        if not isinstance(max_shorturls, int):
            raise PlanAttributeTypeError(
                attr="name", type_expected="str", got=max_shorturls
            )
        if max_shorturls < 0:
            raise ValueError(
                ("The Plan max_shorturls must be greater than or equal to 0, "
                f"got {max_shorturls}")
            )
