from typing import Optional

from .exceptions import PlanAttributeTypeError


class Plan:

    def __init__(self, name: str, max_shorturls: int, id: Optional[int] = None):
        self.validate_id(id)
        self.validate_name(name)
        self.validate_maxshorturls(max_shorturls)

        self._id = id
        self._name = name
        self._max_shorturls = max_shorturls
    
    
    @property
    def id(self):
        return self._id
    
    @property
    def name(self):
        return self._name
    
    @property
    def max_shorturls(self):
        return self._max_shorturls


    @staticmethod
    def validate_id(id):
        if not isinstance(id, (int, type(None))):
            raise PlanAttributeTypeError(
                attr="id", type_expected="int or None", got=id
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
    

    def get_int_id(self) -> int:
        if self.id is None:
            raise ValueError("Plan id is None.")
        else:
            return self.id
