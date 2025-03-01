from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shortener.infra.settings import DATABASE_URL


engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def get_db():
    with Session() as db:
        yield db
