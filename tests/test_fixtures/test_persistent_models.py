import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from shortener.domain.plan import Plan
from shortener.domain.user import User
from shortener.domain.shorturl import ShortURL

from shortener.infra.db.models import PlanModel, UserModel, ShortURLModel


@pytest.mark.asyncio
async def test_persistent_default_plan(
    default_plan: Plan,
    persistent_default_plan: Plan,
    sqlalchemy_session: AsyncSession
):
    assert isinstance(persistent_default_plan, Plan)
    assert persistent_default_plan.name == default_plan.name
    assert await sqlalchemy_session.get(
        PlanModel, persistent_default_plan.pk.get_id()
    ) is not None


@pytest.mark.asyncio
async def test_persistent_eco_plan(
    eco_plan: Plan,
    persistent_eco_plan: Plan,
    sqlalchemy_session: AsyncSession
):
    assert isinstance(persistent_eco_plan, Plan)
    assert persistent_eco_plan.name == eco_plan.name
    assert await sqlalchemy_session.get(
        PlanModel, persistent_eco_plan.pk.get_id()
    ) is not None


@pytest.mark.asyncio
async def test_persistent_normal_user(
    normal_user: User,
    persistent_normal_user: User,
    persistent_normal_shorturl: ShortURL,
    sqlalchemy_session: AsyncSession
):
    assert isinstance(persistent_normal_user, User)
    assert persistent_normal_user.name == normal_user.name
    user_model = await sqlalchemy_session.get(
        UserModel, persistent_normal_user.pk.get_id()
    )
    assert user_model is not None

    shorturls_of_persistent = await persistent_normal_user.get_shorturls()
    shorturls_of_domain = await normal_user.get_shorturls()
    assert len(shorturls_of_persistent) == len(shorturls_of_domain)
    for s1, s2 in zip(shorturls_of_domain, shorturls_of_persistent):
        assert s1.slug == s2.slug


@pytest.mark.asyncio
async def test_persistent_poor_user(
    poor_user: User,
    persistent_poor_user: User,
    sqlalchemy_session: AsyncSession
):
    assert isinstance(persistent_poor_user, User)
    assert persistent_poor_user.name == poor_user.name
    assert await sqlalchemy_session.get(
        UserModel, persistent_poor_user.pk.get_id()
    ) is not None


@pytest.mark.asyncio
async def test_persistent_normal_shorturl(
    normal_shorturl: ShortURL,
    persistent_normal_shorturl: ShortURL,
    sqlalchemy_session: AsyncSession
):
    assert isinstance(persistent_normal_shorturl, ShortURL)
    assert persistent_normal_shorturl.slug == normal_shorturl.slug
    assert await sqlalchemy_session.get(
        ShortURLModel, persistent_normal_shorturl.pk.get_id()
    ) is not None
