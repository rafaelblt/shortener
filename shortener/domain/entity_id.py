from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class EntityID:
    value: UUID

    def __post_init__(self):
        if not isinstance(self.value, UUID):
            raise TypeError(
                f"The {type(self).__name__} value must be an instance of UUID, "
                f"got {type(self.value).__name__}"
            )

    def __str__(self) -> str:
        return str(self.value)
