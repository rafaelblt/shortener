class ModelRelationshipNotLoadedError(Exception):
    def __init__(self, instance: object, attr: str):
        super().__init__(f"Relationship '{attr}' not loaded for {instance}")


class MapperConversionError(Exception): ...
