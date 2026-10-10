from shortener.domain.entity_id import EntityID


class UserID(EntityID):
    """
    Users live outside this service, so their IDs are never generated here.
    See docs/domain.md#owner
    """
