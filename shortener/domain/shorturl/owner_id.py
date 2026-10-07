from shortener.domain.shared.entity_id import EntityID


class OwnerID(EntityID):
    """
    Owners live outside this service, so their IDs are never generated here.
    See docs/domain.md#owner
    """
