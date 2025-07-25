from enum import Enum


class PkType(Enum):
    ID = "id"
    UNDEFINED = "undefined"


class PrimaryKey:
    _value: str
    _type: PkType
    
    @classmethod
    def create_pk_id(cls, id: int):
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
    def pk_type(self):
        return self._type

    def get_id(self):
        if self._type != PkType.ID:
            raise ValueError("The pk is not of type id")
        return int(self._value)
