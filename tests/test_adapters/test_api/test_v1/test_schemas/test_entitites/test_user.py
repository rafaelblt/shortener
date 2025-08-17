from shortener.adapters.api.v1.schemas.entities import PublicUserSchema

from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.user.user import User


def test_public_user_from_domain(normal_user: User):
    normal_user._pk = PrimaryKey.create_pk_id(1)
    normal_user.plan._pk = PrimaryKey.create_pk_id(1)

    retrieved = PublicUserSchema.from_domain(normal_user)
    
    assert retrieved.id == normal_user.pk.get_id()
    assert retrieved.name == normal_user.name
    assert retrieved.email == normal_user.email
    assert retrieved.plan_id == normal_user.plan.pk.get_id()
    assert retrieved.created_at == normal_user.created_at
