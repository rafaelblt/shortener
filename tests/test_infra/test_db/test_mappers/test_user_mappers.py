import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.user import User

from shortener.infra.db.models import  UserModel
from shortener.infra.db.mappers import (
    UserMapper,
    map_user_model_to_domain, map_user_domain_to_model, map_plan_domain_to_model,
)

from tests.utils.entity_helpers import assert_user_fields, serialize_user


def test_map_user_domain_to_model(normal_user: User):
    normal_user.plan._pk = PrimaryKey.create_pk_id(1)

    retrieved = map_user_domain_to_model(normal_user)
    
    assert isinstance(retrieved, UserModel)
    assert_user_fields(retrieved, normal_user)


def test_map_user_model_to_domain(normal_user: User):
    normal_user._pk = PrimaryKey.create_pk_id(1)
    normal_user.plan._pk = PrimaryKey.create_pk_id(1)

    user_model = map_user_domain_to_model(normal_user)
    plan_model = map_plan_domain_to_model(normal_user.plan)
    user_model.plan = plan_model

    retrieved = map_user_model_to_domain(user_model)

    assert isinstance(retrieved, User)
    assert_user_fields(retrieved, normal_user)


@pytest.mark.asyncio
async def test_user_mapper_domain_to_model(normal_user: User, db_session):
    normal_user.plan._pk = PrimaryKey.create_pk_id(1)
    mapper = UserMapper(db_session)

    retrieved = await mapper.domain_to_model(normal_user)
    
    assert isinstance(retrieved, UserModel)
    assert (
        await serialize_user(retrieved, exclude_fields=["shorturls"]) ==
        await serialize_user(normal_user, exclude_fields=["shorturls"])
    )


@pytest.mark.asyncio
async def test_user_mapper_model_to_domain(normal_user: User, db_session: AsyncSession):
    normal_user._pk = PrimaryKey.create_pk_id(1)
    normal_user.plan._pk = PrimaryKey.create_pk_id(1)
    mapper = UserMapper(db_session)

    plan_model = map_plan_domain_to_model(normal_user.plan)
    db_session.add(plan_model)

    user_model = await mapper.domain_to_model(normal_user)
    user_model.plan = plan_model
    db_session.add(user_model)

    await db_session.commit()
    await db_session.refresh(user_model)

    retrieved = await mapper.model_to_domain(user_model)
    
    assert isinstance(retrieved, User)
    assert (
        await serialize_user(retrieved, exclude_fields=["shorturls"]) ==
        await serialize_user(normal_user, exclude_fields=["shorturls"])
    )
