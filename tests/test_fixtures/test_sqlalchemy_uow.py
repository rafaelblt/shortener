from shortener.infra.db.sqlalchemy_uow import SQLAlchemyUnitOfWork


def test_sqlalchemy_uow(sqlalchemy_uow):
    assert isinstance(sqlalchemy_uow, SQLAlchemyUnitOfWork)
