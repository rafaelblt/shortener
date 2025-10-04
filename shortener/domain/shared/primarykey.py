from enum import Enum


class PkType(Enum):
    ID = "id"
    UNDEFINED = "undefined"


class PrimaryKey:
    _value: str
    _type: PkType
    
    @classmethod
    def create_pk_id(cls, id: int):
        if not isinstance(id, int):
            raise TypeError("PrimaryKey ID must be int")
        pk = cls()
        pk._value = str(id)
        pk._type = PkType.ID
        return pk
    
    @classmethod
    def create_pk_undefined(cls):
        pk = cls()
        pk._value = ""
        pk._type =  PkType.UNDEFINED
        return pk

    @property
    def raw_value(self):
        return self._value

    @property
    def pk_type(self):
        return self._type
    
    def is_undefined(self):
        return self.pk_type == PkType.UNDEFINED
    
    def is_id(self):
        return self.pk_type == PkType.ID

    def get_id(self):
        if self._type != PkType.ID:
            raise ValueError("The pk is not of type id")
        return int(self._value)
    
    def __eq__(self, other_obj: object) -> bool:
        if not isinstance(other_obj, PrimaryKey):
            return NotImplemented
        return (self.raw_value, self.pk_type) == (other_obj.raw_value, other_obj.pk_type)
    
    def __str__(self) -> str:
        return self.raw_value or "None"

    def __repr__(self) -> str:
        return f"<PrimaryKey Raw={self.raw_value} PkType={self.pk_type}>"
