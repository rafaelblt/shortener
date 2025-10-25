from shortener.infra.db.repositories import (
    SQLAlchemyShortURLRepository,
    SQLAlchemyUserRepository,
    SQLAlchemyPlanRepository,
)


def test_sqlalchemy_shorturl_repository(sqlalchemy_shorturl_repository, sqlalchemy_session):
    assert isinstance(sqlalchemy_shorturl_repository, SQLAlchemyShortURLRepository)
    assert sqlalchemy_shorturl_repository.session == sqlalchemy_session


def test_sqlalchemy_user_repository(sqlalchemy_user_repository, sqlalchemy_session):
    assert isinstance(sqlalchemy_user_repository, SQLAlchemyUserRepository)
    assert sqlalchemy_user_repository.session == sqlalchemy_session


def test_sqlalchemy_plan_repository(sqlalchemy_plan_repository, sqlalchemy_session):
    assert isinstance(sqlalchemy_plan_repository, SQLAlchemyPlanRepository)
    assert sqlalchemy_plan_repository.session == sqlalchemy_session
